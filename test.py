from flv_tool import FlvReader

f = open(r'your_video.flv','rb')
reader = FlvReader(f)
flv = reader.read_flv()

print(flv.body[1].py_native_value)

