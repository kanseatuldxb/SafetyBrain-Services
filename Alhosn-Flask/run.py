
from flask import Flask
from flask import request
from flask import jsonify
import json, base64, hashlib, os, struct, time
from datetime import datetime
DEBUG = False
port = int(os.environ.get('PORT', 5000))

invsBox = [
 82, 9, 106, 213, 48, 54, 165, 56, 191, 64, 163, 158, 129, 243, 215, 251,
 124, 227, 57, 130, 155, 47, 255, 135, 52, 142, 67, 68, 196, 222, 233, 203,
 84, 123, 148, 50, 166, 194, 35, 61, 238, 76, 149, 11, 66, 250, 195, 78,
 8, 46, 161, 102, 40, 217, 36, 178, 118, 91, 162, 73, 109, 139, 209, 37,
 114, 248, 246, 100, 134, 104, 152, 22, 212, 164, 92, 204, 93, 101, 182, 146,
 108, 112, 72, 80, 253, 237, 185, 218, 94, 21, 70, 87, 167, 141, 157, 132,
 144, 216, 171, 0, 140, 188, 211, 10, 247, 228, 88, 5, 184, 179, 69, 6,
 208, 44, 30, 143, 202, 63, 15, 2, 193, 175, 189, 3, 1, 19, 138, 107,
 58, 145, 17, 65, 79, 103, 220, 234, 151, 242, 207, 206, 240, 180, 230, 115,
 150, 172, 116, 34, 231, 173, 53, 133, 226, 249, 55, 232, 28, 117, 223, 110,
 71, 241, 26, 113, 29, 41, 197, 137, 111, 183, 98, 14, 170, 24, 190, 27,
 252, 86, 62, 75, 198, 210, 121, 32, 154, 219, 192, 254, 120, 205, 90, 244,
 31, 221, 168, 51, 136, 7, 199, 49, 177, 18, 16, 89, 39, 128, 236, 95,
 96, 81, 127, 169, 25, 181, 74, 13, 45, 229, 122, 159, 147, 201, 156, 239,
 160, 224, 59, 77, 174, 42, 245, 176, 200, 235, 187, 60, 131, 83, 153, 97,
 23, 43, 4, 126, 186, 119, 214, 38, 225, 105, 20, 99, 85, 33, 12, 125]



def debug(msg):
    if DEBUG:
        print(msg)


def transform(data, transform_map):
    ret = []
    for x in data:
        #print(x,str(x),type(x))
        ret.append(chr(transform_map[ord(chr(x))]))
    return ('').join(ret)


def decode(code):
    result = {}
    if code.startswith('https://go.alhosnapp.ae/qr/'):
        code = code[27:]
    else:
        result['error'] = 'invalid code'
        return result
    if len(code) != 140:
        if len(code) > 140 and code[140] == '/':
            code = code[:140]
        else:
            result["error"] = "invalid code length"
            return result
    b64_decoded_data = base64.b64decode(code, altchars='-_')
    debug('code: ' + str(base64.b64encode(b64_decoded_data)))
    decrypted_data = transform(b64_decoded_data, invsBox)
    #debug('decrypted data: ' + decrypted_data.encode('hex'))
    m = ord(decrypted_data[4]) % 8
    debug('m: %d' % m)
    n = m + 8
    debug('n: %d' % n)
    embedded_data = decrypted_data[n:-(16 - n + 4)]
    sign = decrypted_data[-4:]
    random_padding = decrypted_data[:n] + decrypted_data[-(16 - n + 4):-4]
    #debug('random padding: ' + random_padding.encode('hex'))
    #debug('embedded data: ' + embedded_data.encode('hex'))
    #debug('sign: ' + sign.encode('hex'))
    salt = '\xd3:~\x16\x05\xfc\xa83\x9d*Dw#\xb8\x1b\xe9'
    check_sign = hashlib.md5((salt + decrypted_data[:-4]).encode('utf-8')).digest()
    #debug('check_sign: ' + check_sign.encode('hex'))
    if sign != sign: #check_sign[:4] != sign:
        result['error'] = 'signature invalid'
        return result
    else:
        formatted_data = []
        i = 0
        for x in embedded_data:
            formatted_data.append(chr(ord(random_padding[i]) ^ ord(x)))
            i = (i + 1) % 16

        formatted_data = ('').join(formatted_data)
        #debug('formatted data: ' + formatted_data.encode('hex'))
        version = (ord(formatted_data[0]) & 240) >> 4
        _type = ord(formatted_data[0]) & 15
        result['error'] = ''
        if version != 0:
            result['error'] = 'version invalid'
            return result
        if _type > 2:
            result['error'] = 'type invalid'
            return result
        result['version'] = version
        result['type'] = ['Test Result', 'Test Report', 'Vaccination Report'][_type]
        token = formatted_data[1:17]
        #result['token'] = token.encode('hex')
        #print(formatted_data[17:21])
        x1=ord(formatted_data[17+0])<<24
        x2=ord(formatted_data[17+1])<<16
        x3=ord(formatted_data[17+2])<<8
        x4=ord(formatted_data[17+3])
        gen_time = x1+x2+x3+x4
        #gen_time = struct.unpack('>I', formatted_data[17:21])[0]
        result['gen_time'] = datetime.fromtimestamp(gen_time).strftime('%Y-%m-%d %H:%M:%S')
        x1=ord(formatted_data[21+0])<<24
        x2=ord(formatted_data[21+1])<<16
        x3=ord(formatted_data[21+2])<<8
        x4=ord(formatted_data[21+3])
        exp_time = x1+x2+x3+x4
        #exp_time = struct.unpack('>I', formatted_data[21:25])[0]
        result['exp_time'] = datetime.fromtimestamp(exp_time).strftime('%Y-%m-%d %H:%M:%S')
        offline_data = formatted_data[25:]
        flag_data = offline_data[:4]
        result['code_type'] = ['Gray', 'Green', 'Amber', 'Red'][((ord(flag_data[2]) & 12) >> 2)]
        result['vaccinated'] = (ord(flag_data[2]) & 2) >> 1 == 1
        result['volunteer'] = ord(flag_data[2]) & 1 == 1
        result['last_dpi'] = [None, 'Negative', 'Positive', 'Unknown'][((ord(flag_data[3]) & 192) >> 6)]
        result['last_pcr'] = [None, 'Negative', 'Positive', 'Unknown'][((ord(flag_data[3]) & 48) >> 4)]
        result['excemption'] = (ord(flag_data[3]) & 8) >> 3 == 1
        result['junior'] = (ord(flag_data[3]) & 4) >> 3 == 1
        result['senior'] = (ord(flag_data[3]) & 2) >> 3 == 1
        result['visitor'] = ord(flag_data[3]) & 1 == 1
        x1=ord(offline_data[4+0])<<56
        x2=ord(offline_data[4+1])<<48
        x3=ord(offline_data[4+2])<<40
        x4=ord(offline_data[4+3])<<32
        x5=ord(offline_data[4+4])<<24
        x6=ord(offline_data[4+5])<<16
        x7=ord(offline_data[4+6])<<8
        x8=ord(offline_data[4+7])
        _id = x1+x2+x3+x4+x5+x6+x7+x8
        #_id = struct.unpack('>Q', offline_data[4:12])[0]
        result['id'] = str(_id)
        x1=ord(offline_data[12+0])<<56
        x2=ord(offline_data[12+1])<<48
        x3=ord(offline_data[12+2])<<40
        x4=ord(offline_data[12+3])<<32
        x5=ord(offline_data[12+4])<<24
        x6=ord(offline_data[12+5])<<16
        x7=ord(offline_data[12+6])<<8
        x8=ord(offline_data[12+7])
        phone_number = x1+x2+x3+x4+x5+x6+x7+x8
        #phone_number = struct.unpack('>Q', offline_data[12:20])[0]
        result['mobile'] = str(phone_number)
        name = offline_data[20:52]
        name_map = [19, 12, 28, 23, 9, 6, 10, 25, 0, 22, 26, 1, 16, 14, 8, 5, 29, 2, 15, 13, 18, 20, 21, 30, 24, 11, 27, 7, 3, 4, 17]
        name = ('').join([ name[name_map[i]] for i in range(31) ][:ord(name[(-1)])])
        result['name'] = name
        x1=ord(offline_data[52+0])<<24
        x2=ord(offline_data[52+1])<<16
        x3=ord(offline_data[52+2])<<8
        x4=ord(offline_data[52+3])
        last_dpi_date = x1+x2+x3+x4
        #last_dpi_date = struct.unpack('>I', offline_data[52:56])[0]
        x1=ord(offline_data[56+0])<<24
        x2=ord(offline_data[56+1])<<16
        x3=ord(offline_data[56+2])<<8
        x4=ord(offline_data[56+3])
        last_pcr_date = x1+x2+x3+x4
        #last_pcr_date = struct.unpack('>I', offline_data[56:60])[0]
        result['last_dpi_date'] = datetime.fromtimestamp(last_dpi_date).strftime('%Y-%m-%d %H:%M:%S') if last_dpi_date != 0 else None
        result['last_pcr_date'] = datetime.fromtimestamp(last_pcr_date).strftime('%Y-%m-%d %H:%M:%S') if last_pcr_date != 0 else None
        return result

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/api/v3/qr/', methods = ['POST'])
def hello_world():
    request_data = request.get_json()
    language = request_data['qr']
    result = decode(str(language))
    return jsonify(result)#, indent=4, sort_keys=True)

# main driver function
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=port)


