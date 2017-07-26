import itchat, time
from itchat.content import *
import requests

#Tuling robot replys text messages when it not from a group chat
#启动图灵机器人自动回复文本等类别的非群聊消息
KEY = '15b17d6d9551429cb3a6fd3c1059044a'

def get_response(msg):
    apiUrl = 'http://www.tuling123.com/openapi/api'
    data = {
        'key'    : KEY,
        'info'   : msg,
        'userid' : 'wechat-robot',
    }
    try:
        r = requests.post(apiUrl, data=data).json()
        return r.get('text')
    except:
        return

@itchat.msg_register(itchat.content.TEXT)
def tuling_reply(msg):
    defaultReply = 'I received: ' + msg['Text']
    reply = get_response(msg['Text'])
    return reply or defaultReply

# 自动处理添加好友申请
@itchat.msg_register(FRIENDS)
def add_friend(msg):
	itchat.add_friend(**msg['Text']) # 该操作会自动将新好友的消息录入，不需要重载通讯录
	itchat.send_msg(u'你好哇。平时这里驻守一只二狗子陪你聊天，还可以讲笑话。', msg['RecommendInfo']['UserName'])

# 自动回复文本等类别的群聊消息
# isGroupChat=True表示为群聊消息
#如果在群聊中被at
@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
    if msg.isAt:
        msg.user.send(u'@%s\u2005I received: %s' % (
            msg.actualNickName, msg.text))

@itchat.msg_register([TEXT, SHARING], isGroupChat=True)
def group_reply_text(msg):
	# 消息来自于哪个群聊
	chatroom_id = msg['FromUserName']
	print('chatroom_id:',chatroom_id.encode())
	# 发送者的群内昵称
	username = msg['ActualNickName']
	print('群内昵称:',username)
	#发送者所在的群名称
	#chatroomname = msg['NickName']
	#print('群名称',chatroomname)


	# 消息并不是来自于需要同步的群
	if not chatroom_id in chatroom_ids:
		return

	if msg['Type'] == TEXT:
		content = msg['Content']
	elif msg['Type'] == SHARING:
		content = msg['Text']

	# 根据消息类型转发至其他需要同步消息的群聊
	if msg['Type'] == TEXT:
		for item in chatrooms:
			if not item['UserName'] == chatroom_id:
				itchat.send('%s:\n%s' % (username, msg['Content']), item['UserName'])
	elif msg['Type'] == SHARING:
		for item in chatrooms:
			if not item['UserName'] == chatroom_id:
				itchat.send('%s\n%s\n%s' % (username, msg['Text'], msg['Url']), item['UserName'])

# 自动回复图片等类别的群聊消息
# isGroupChat=True表示为群聊消息
@itchat.msg_register([PICTURE, ATTACHMENT, VIDEO], isGroupChat=True)
def group_reply_media(msg):
	# 消息来自于哪个群聊
	chatroom_id = msg['FromUserName']
	# 发送者的昵称
	username = msg['ActualNickName']

	# 消息并不是来自于需要同步的群
	if not chatroom_id in chatroom_ids:
		return

	# 如果为gif图片则不转发
	if msg['FileName'][-4:] == '.gif':
		return

	# 下载图片等文件
	msg['Text'](msg['FileName'])
	# 转发至其他需要同步消息的群聊
	for item in chatrooms:
		if not item['UserName'] == chatroom_id:
			itchat.send('@%s@%s' % ({'Picture': 'img', 'Video': 'vid'}.get(msg['Type'], 'fil'), msg['FileName']), item['UserName'])

#log in via QR code
# 扫二维码登录
itchat.auto_login(hotReload=True)
# 获取所有通讯录中的群聊
# 需要在微信中将需要同步的群聊都保存至通讯录
chatrooms = itchat.get_chatrooms(update=True, contactOnly=True)
chatroom_ids = [c['UserName'] for c in chatrooms]
print('正在监测的群聊：', len(chatrooms), '个')
print(' '.join([item['NickName'] for item in chatrooms]))
# 开始监测

itchat.run()
