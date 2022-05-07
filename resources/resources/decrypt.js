const {createHash} = require('crypto');

function convertFromHex(hex) {//Thanks stackoverflow!
    var hex = hex.toString();
    var str = '';
    for (var i = 0; i < hex.length; i += 2)
        str += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
    return str;
}

function convertHexStringToNumArray(h) {//From puffco's source
    var i, j = (i = h.match(/.{2}/g)) != null ? i : [];
    return j == null ? void 0x0 : j.map(function(k) {
        return parseInt(k, 0x10);
    });
}

var initialAccessSeedKey, DEVICE_HANDSHAKE_DECODED, newAccessSeedArray, newKeyIndex, newAccessSeedKeyHashed, finalAccessSeedKey;

const args = process.argv;
key = args.slice(2)

initialAccessSeedKey = key; //an AccessSeedKey I used while testing. You can get this from 'E0' characteristic. This is never the same and changes upon connecting.

DEVICE_HANDSHAKE_DECODED = convertFromHex(Buffer.from('FUrZc0WilhUBteT2JlCc+A==', 'base64').toString('hex'));


newAccessSeedArray = new Uint8Array(0x20); //Create 32bit Uint8Array

for (newKeyIndex = 0x0; newKeyIndex < 0x10; ++newKeyIndex) { //Loop, creating new 32bit key
    newAccessSeedArray[newKeyIndex] = DEVICE_HANDSHAKE_DECODED.charCodeAt(newKeyIndex);//adding DEVICE_HANDSHAKE to first 16 bits
    newAccessSeedArray[newKeyIndex + 0x10] = initialAccessSeedKey[newKeyIndex];//adding accessSeedKey to last 16 bits
}
newAccessSeedKeyHashed = convertHexStringToNumArray(createHash('sha256').update(newAccessSeedArray).digest('hex')); //hash to sha256 and convert the new AccessSeedKey to a num array
finalAccessSeedKey = newAccessSeedKeyHashed.slice(0x0, 0x10); //Slice and only use first 16 bits

console.log(finalAccessSeedKey); //Print new accessSeedKey
