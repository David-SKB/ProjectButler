#!/usr/bin/python3
import socket
import time
import datetime
import os
import sys
import threading

#Connection Stuff
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "pool.irc.tl" # Server
home_channel = "#batcave" # Channel
admin_echo_channel = "#lvcnr.admins"
echo_channel = "#lvcnr.echo"
channel_group = ["#lvcnr"]
botnick = "Alfred" # Your bots nick
adminname = "Bruce_Bond" #Your IRC nickname.
exitcode = "bye " + botnick.lower()
password = "OMITTED"
ircsock.connect((server, 6667)) # Connect to the server on port 6667
ircsock.send(bytes("USER "+ botnick +" "+ password +" "+ botnick + " " + botnick + "\n")) # Saying to set all the fields to the bot nickname.
ircsock.send(bytes("NICK "+ botnick +"\n")) # Assign the nick to the bot

#GLOBAL VARS
in_session = True
trackers = 0
tracker_target_list = []
kcnr_jessica_bots = ["Jessica", "Jessica2", "Jessica3"]
admin_list = ["kar", "peter", "fuet", "aimandkill", "police_force", "torque", "edmundxx", "ryanlml", "[rw]joel", "bruce_bond", "forcezx", "shane", "kruthal", "sycro"]
misc_message_list = ["GRIM REAPER", "TURF", "TICKET", "SERVER KICK", "LOTTERY", "HIT CONTRACT", "ADMIN BAN", "SERVER BAN", "ROBBERY", "NEWS", "MONEY BAG", "WEEK CHANGE", "KIDNAP", "WHISPER", "PM"]
stopwatch_list = [] #[username, starttime]
timer_list = [] #[username, ,duration, starttime, reply_type, msg_channel]
activator = "?"# Symbol used for executing commands
bot_start_time = time.time()
max_trackers = 1
say_syntax = "!say" # Syntax for speaking ingame from irc
admin_say_syntax = "@" # 
ingame_pm_syntax = "!pm" # Syntax for sending pm's from irc
time.sleep(5)


def connect(): # does initial shit
	ircsock.send ("PRIVMSG NickServ :identify OMITTED \n")
	joinchan(home_channel, "OMITTED")
	joinchan(admin_echo_channel, "OMITTED")
	joinchan(echo_channel)
	
	for chan in channel_group:
		joinchan(chan)
	
	
def joinchan(chan, chan_pass = ""): # join channel(s).
	ircsock.send(bytes("JOIN "+ chan + " " + chan_pass + "\n")) 
	#print("JOIN "+ chan + " " + chan_pass + "\n")
	ircmsg = ""
	chan_joined = True
	while ircmsg.find("End of /NAMES list.") == -1:  
		ircmsg = ircsock.recv(2048).decode("UTF-8")
		ircmsg = ircmsg.strip('\n\r')
		if ircmsg.find(":Cannot join channel (Incorrect channel key)") != -1:
			chan_joined = False
			#print(ircmsg)
			break
		#print(ircmsg)
	return chan_joined
		
		
def leavechan(chan): # leave channel(s).
	ircsock.send(bytes("PART {0} \r\n".format(chan)))
	
	
def ping(pingval): # respond to server Pings.
	ircsock.send(bytes("PONG :" + pingval + "\n"))
	print("PONG :" + pingval)

	
def sendmsg(msg, name, reply_type, msg_channel = home_channel): # Sends messages.
	
	# IRC CHANNEL
	if reply_type == 1:
		ircsock.send(bytes("PRIVMSG "+ msg_channel +" :"+ msg +"\n"))
		
	# IRC PM
	if reply_type == 2:
		ircsock.send(bytes("PRIVMSG "+ name +" :"+ msg +"\n"))
		
	# INGAME CHAT
	elif reply_type == 3:
		msg = say_syntax + " " + msg
		ircsock.send(bytes("PRIVMSG "+ echo_channel +" :"+ msg +"\n"))
		
	# INGAME ADMIN CHAT
	elif reply_type == 4:
		msg = admin_say_syntax + msg
		ircsock.send(bytes("PRIVMSG "+ admin_echo_channel +" :"+ msg +"\n"))
		
	# INGAME PM CHAT - TODO
	elif reply_type == 5:
		msg = ingame_pm_syntax + " " + name + " " + msg
		ircsock.send(bytes("PRIVMSG "+ admin_echo_channel +" :"+ msg +"\n"))
	

	
def is_ingame_message(name):
	if name in kcnr_jessica_bots:
		return True
	else:
		return False
		
#Returns the message source channel for ingame messages		
def get_message_channel(message):
	chan_name = message.split('PRIVMSG',1)[1].split(' ', 2)[1].strip('\n\r').split('#', 1)[1]
	msg_channel = "#" + chan_name
	return msg_channel

		
def get_irc_message():
	try: 
		ircmsg = ircsock.recv(2048).decode("UTF-8")
		ircmsg = ircmsg.strip('\n\r')
		#print(ircmsg)
		return ircmsg
	except (UnicodeDecodeError, UnicodeEncodeError) as e:
		print("Invalid Characters")
		return "NULL"
		
def check_if_query(message):
	msg_head = message.split('PRIVMSG',1)[1].split(' ', 2)[1].strip('\n\r')
	if msg_head.find("#") != -1:
		return False
	else:
		return True

	

#Main Body  
def main():
	global in_session
	is_query = False
	
	while in_session:
		
		ircmsg = get_irc_message()
		
		# [NORMAL IRC MESSAGE]
		if ircmsg.find("PRIVMSG") != -1:

			name = ircmsg.split('!',1)[0][1:]
			message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
			is_query = check_if_query(ircmsg)
			
			# Check if valid
			if len(name) < 17:
			
			
			
				# [NON-QUERY MESSAGE] # - Most likely scenario
				if not is_query:
				
				
					# [INGAME MESSAGE] #
					if is_ingame_message(name):
						source_channel = get_message_channel(ircmsg)
						
						# [ADMIN ECHO MESSAGE]
						if source_channel == admin_echo_channel:
	
							# [ADMIN CHAT]
							if message[:17].find("(Admin Chat)"):
								try:
									admin_name = remove_id(message[21:].split(":")[0])
									admin_message = message.split(": ")[1]
									
									# [POSSIBLE COMMAND]
									if admin_message.startswith(activator):
										
										# [COMMAND CHECK]
										if not check_command(admin_message, admin_name, 4):
											tracker_scan(message)  # Scan for tracked targets

									# [REGULAR ADMIN ECHO MESSAGE]
									else:
										msg_start = message[:20]
										if msg_start.find("[ADMIN BAN]") != -1 or msg_start.find("[GRIM REAPER ") != -1:
											pass
										else:
											tracker_scan(message)  # Scan for tracked targets
										
								except IndexError:
									tracker_scan(message)  # Scan for tracked targets
									
							else:
								tracker_scan(message)  # Scan for tracked targets
						
						# [ECHO MESSAGE]
						else:
							msg_start = message[:20]
							misc_found = False
								
							if message.startswith("***"):
								pass  # !say message, already logged, ignore
								
							elif message.find(":"):
								try:
									player_name = message.split(":")[0][::-1].split("(", 2)[-1][::-1]
									player_message = message.split(": ")[1]
									
									# [POSSIBLE COMMAND]
									if player_message.startswith(activator):
										
										# [COMMAND CHECK]
										if not check_command(player_message, player_name, 3):
											tracker_scan(message)  # Scan for tracked targets

									# [REGULAR ECHO MESSAGE]
									else:
										tracker_scan(message)  # Scan for tracked targets
										
								except IndexError:
									tracker_scan(message)  # Scan for tracked targets

									
									
					# [IRC MESSAGE] #
					else:
						msg_channel = get_message_channel(ircmsg)
						
						# [POSSIBLE COMMAND]
						if message.startswith(activator):
							# [COMMAND CHECK]
							if not check_command(message, name, 1, msg_channel):
								tracker_scan(message)  # Scan for tracked targets
						
						# [REGULAR IRC MESSAGE]
						else:
							tracker_scan(message)  # Scan for tracked targets
				
					timer_scan()# Check if any timers have expired
				
				# [QUERY MESSAGE] # - Unlikely scenario - TODO: CHECK FOR JESSICA PMS FROM INGAME
				else:				
					# [POSSIBLE COMMAND]
					if message.startswith(activator):
						
						# [COMMAND CHECK]
						check_command(message, name, 2)
			
		# [PING MESSAGE]
		elif ircmsg.find("PING :") != -1:
			print("PINGMSG > " + ircmsg)
			pingval = ircmsg.split('PING',1)[1].split(':',1)[1]
			ping(pingval)#Send PONG


		#[MISC MESSAGE]
		else: 
			if ircmsg.find("This nickname is registered") != -1:
				#Identify and Join
				connect()
			if len(ircmsg) == 0:
				print("TIMEOUT - ATTEMPTING TO RESTART")
				time.sleep(5)
				in_session = False
				cmd_restart("", 1, home_channel)
				time.sleep(2)
			

def remove_id(name):
	return name[::-1].split("(", 1)[-1][::-1]
				
							
def uptime(val):
 
	if val == 0:#VPS Uptime
		try:
			f = open( "/proc/uptime" )
			contents = f.read().split()
			f.close()
		except:
			return "Cannot open uptime file: /proc/uptime"
		total_seconds = float(contents[0])
	else:#Alfred Uptime
		total_seconds = time.time() - bot_start_time
 
	# Helper vars:
	MINUTE  = 60
	HOUR    = MINUTE * 60
	DAY     = HOUR * 24

	# Get the days, hours, etc:
	days    = int( total_seconds / DAY )
	hours   = int( ( total_seconds % DAY ) / HOUR )
	minutes = int( ( total_seconds % HOUR ) / MINUTE )
	seconds = int( total_seconds % MINUTE )

	# Build up the pretty string (like this: "N days, N hours, N minutes, N seconds")
	string = ""
	if days > 0:
		string += str(days) + " " + (days == 1 and "day" or "days" ) + ", "
	if len(string) > 0 or hours > 0:
		string += str(hours) + " " + (hours == 1 and "hour" or "hours" ) + ", "
	if len(string) > 0 or minutes > 0:
		string += str(minutes) + " " + (minutes == 1 and "minute" or "minutes" ) + ", "
	string += str(seconds) + " " + (seconds == 1 and "second" or "seconds" )

	return string;

	
def time_of_day(): # HELPER: tell greeting
	currentTime = datetime.datetime.now()
	currentTime.hour
	tod = ""
	if currentTime.hour < 12:
		tod = "morning"
	elif 12 <= currentTime.hour < 18:
		tod = "afternoon"
	else:
		tod = evening
	return(tod)

def track(target): # Tracks messages for the target.
	tracker_target_list.append(target)
	global trackers
	trackers += 1
	
def untrack(target): # Untracks messages for the target.
	tracker_target_list.remove(target)
	global trackers
	trackers -= 1
	
# HELPER: checks if user is an admin.
def is_admin(user): 
	if user.lower() in admin_list:
		return True
	else:
		return False
		
# Scan message to see if tracked target is mentioned
def tracker_scan(message):
	for track_target in tracker_target_list:
		if message.find(track_target) != -1:
			track_msg =  "[\x02" + track_target + "\x02] " + message
			sendmsg(track_msg, "", 1, home_channel)
		
def timer_scan():
	for timer_item in timer_list:#[username, ,duration, starttime, reply_type, msg_channel]
		time_remaining = timer_item[1] - (time.time() - timer_item[2])
		if time_remaining <= 1:
			message = "[\x02TIMER ENDED\x02] \x02User:\x02 " + timer_item[0] + " \x02Duration:\x02 " + time.strftime('%H:%M:%S', time.gmtime(timer_item[1]))
			timer_list.remove(timer_item)
			sendmsg(message, timer_item[0], timer_item[3], timer_item[4])
		
		
# Here we check for commands and execute if found	
def check_command(message, name, reply_type, msg_channel = ""):
	
	# [CMDS COMMAND]
	if message[:5].lower().find(activator + 'cmds') != -1 and len(message) == 5:
		cmd_cmds(name, reply_type)
		return True
	
	# [STOPWATCH COMMAND]
	elif message[:10].lower().find(activator + 'stopwatch') != -1 and len(message) == 10:
		cmd_stopwatch(name, reply_type, msg_channel)
		return True
		
	# [TIMER COMMAND]
	elif message[:7].find(activator + 'timer') != -1 and message[6] == " ":
		cmd_timer(message, name, reply_type, msg_channel)
		return True
	
	# [STOPTIMER COMMAND]
	elif message[:10].lower().find(activator + 'stoptimer') != -1 and len(message) == 10:
		cmd_stoptimer(name, reply_type, msg_channel)
		return True
	
	# [UPTIME COMMAND]
	elif message[:7].lower().find(activator + 'uptime') != -1 and len(message) == 7:
		cmd_uptime(name, reply_type, msg_channel, 1)
		return True
		
	# [SUPTIME COMMAND]
	elif message[:8].lower().find(activator + 'suptime') != -1 and len(message) == 8 and is_admin(name):
		cmd_uptime(name, reply_type, msg_channel, 0)
		return True
		
	# [JOIN COMMAND]
	elif message[:6].find(activator + 'join') != -1 and message[5] == " " and is_admin(name):
		cmd_join(message, name, reply_type, msg_channel)
		return True
		
	# [LEAVE COMMAND]
	elif message[:7].find(activator + 'leave') != -1 and message[6] == " " and is_admin(name):
		cmd_leave(message, name, reply_type, msg_channel)
		return True
		
	# [TRACKERS COMMAND]
	elif message[:9].lower().find(activator + 'trackers') != -1 and len(message) == 9 and is_admin(name):
		cmd_trackers(name, reply_type)
		return True
		
	# [TRACK COMMAND]
	elif message[:7].find(activator + 'track') != -1 and message[6] == " " and is_admin(name):
		cmd_track(message, name, reply_type, msg_channel)
		return True
	
	# [UNTRACK COMMAND]
	elif message[:9].find(activator + 'untrack') != -1 and message[8] == " " and is_admin(name):
		cmd_untrack(message, name, reply_type, msg_channel)
		return True
		
	# [TELL COMMAND]
	elif message[:5].find(activator + 'tell') != -1 and is_admin(name):
		cmd_tell(message, name)
		return True
		
	# [RESTART COMMAND]
	elif message[:8].lower().find(activator + 'restart') != -1 and len(message) == 8 and is_admin(name):
		cmd_restart(name, reply_type, msg_channel)
		return True
		
	# [QUIT COMMAND]
	elif message[:5].lower().find(activator + 'quit') != -1 and len(message) == 5 and is_admin(name):
		cmd_quit(msg_channel, name, reply_type, 1)
		return True
	
	#[NOT A COMMAND]
	else:
		return False

		
# Talk using Alfred
def cmd_tell(message, name):
	if len(message) > 6 and message[5] == " ":
		target = message.split(' ', 1)[1]
		if target.find(' ') != -1:
			target_message = target.split(' ', 1)[1]
			target = target.split(' ')[0]
		else:
			message = "Could not parse. The message should be in the format of '.tell [target] [message]' to work properly."
			return
	else:
		message = "Could not parse. The message should be in the format of '.tell [target] [message]' to work properly."
		return
	sendmsg(target_message, target, 2)
	
	
# Start / stop stopwatch
def cmd_stopwatch(name, reply_type, msg_channel):	
	stopwatch_found = False
	found_item = []	#[username, starttime]			

	for item in stopwatch_list:
		try:
			if item.index(name) != -1:
				stopwatch_found = True
				found_item = item
				break
		except ValueError:
			pass # Do nothing
			
	if stopwatch_found:
		# [START TIMER]
		elapsed_time = time.strftime('%H:%M:%S', time.gmtime(time.time() - found_item[1]))
		message = "Time Elapsed: " + elapsed_time
		#print(found_item[1])
		stopwatch_list.remove(found_item)
	else:
		# [STOP TIMER]
		message = "Stopwatch Started [" + name + "] - Stop with " + activator + "stopwatch"
		stopwatch_list.append([name, time.time()])

	if reply_type == 3:
		sendmsg(message, name, 5)
	else:
		sendmsg(message, name, reply_type, msg_channel)
	
	
# Starts timer for user
def cmd_timer(message, name, reply_type, msg_channel):
	if len(message) > 7:
		timer_length = message.split(' ', 1)[1]

		if reply_type == 3:
			reply_type = 5
		
		if timer_length.find(' ') != -1:
			message = "Could not start. Correct usage: " + activator + "timer [seconds]"
		else:
			try:
				timer_int_duration = int(timer_length)
				if timer_int_duration < 1:
					message = "Please choose a valid length of time [seconds]."
				else:
					timer_found = False
					found_item = [] #[username, duration, starttime, reply_type, msg_channel]				

					for item in timer_list:
						try:
							if item.index(name) != -1:
								timer_found = True
								found_item = item
								break
						except ValueError:
							timer_found = False
					
					if timer_found:
						time_remaining = found_item[1] - (time.time() - found_item[2])
						message = "[TIMER ACTIVE] User: " + name + " Time Remaining: " + time.strftime('%H:%M:%S', time.gmtime(time_remaining)) + ". Cancel with " + activator + "stoptimer"
					else:
						timer_list.append([name, timer_int_duration, time.time(), reply_type, msg_channel])
						message = "[TIMER STARTED] User: " + name + " Duration: " + time.strftime('%H:%M:%S', time.gmtime(timer_int_duration))
					
			except ValueError:
				message = "Could not start. Correct usage: " + activator + "timer [seconds]"										
	else:
		message = "Could not start. Correct usage: " + activator + "timer [seconds]"
	
	sendmsg(message, name, reply_type, msg_channel)
	
	
#Stops user's active timer
def cmd_stoptimer(name, reply_type, msg_channel):
	timer_found = False
	found_item = [] #[username, duration, starttime]				

	for item in timer_list:
		try:
			if item.index(name) != -1:
				timer_found = True
				found_item = item
				break
		except ValueError:
			timer_found = False
		
	if timer_found:
		time_remaining = found_item[1] - (time.time() - found_item[2])
		message = "[\x02TIMER STOPPED\x02] \x02User:\x02 " + found_item[0] + " \x02Time Remaining:\x02 " + time.strftime('%H:%M:%S', time.gmtime(time_remaining))
		timer_list.remove(found_item)
	else:
		message = "Timer not found. Start using ?timer"
		
	sendmsg(message, name, reply_type, msg_channel)
	
	
# Check Alfred / VPS Uptime
def cmd_uptime(name, reply_type, msg_channel, target):
	bot_end_time = time.time()
	if target == 0:
		message = "Current uptime [VPS]: " + uptime(target)
	else:
		message = "Current uptime [BOT]: " + uptime(target)
	
	sendmsg(message, name, reply_type, msg_channel)

	
# Join specified channel
def cmd_join(message, name, reply_type, msg_channel):
	if len(message) > 6:
		chan_pass = ""
		target = message.split(' ', 1)[1]
		if target.find(' ') != -1:
			chan_pass = target.split(' ', 1)[1]
			target = target.split(' ', 1)[0]
			if joinchan(target, chan_pass):
				message = "Joined Channel: " + target
			else:
				message = "Join Failed: " + target
		else:
			if joinchan(target):
				message = "Joined Channel: " + target
			else:
				message = "Join Failed: " + target
	else:
		message = "Correct usage: " + activator + "join [#channel]"
		
		if reply_type == 3:
			sendmsg(message, name, 5, msg_channel)
		else:
			sendmsg(message, name, reply_type, msg_channel)

			
# Leave specified channel
def cmd_leave (message, name, reply_type, msg_channel):
	if len(message) > 7:
		target = message.split(' ', 1)[1]
		if target.find(' ') != -1:
			message = "Correct usage: " + activator + "leave [#channel]"
		else:
			leavechan(target)
			message = "Channel Left: " + target
	else:
		message = "Correct usage: " + activator + "leave [#channel]"
	
	if reply_type == 3:
		sendmsg(message, name, 5, msg_channel)
	elif reply_type == 1:
		sendmsg(message, name, 2, msg_channel)
	else:
		sendmsg(message, name, reply_type, msg_channel)
	
	
#List tracked targets
def cmd_trackers(name, reply_type):
	if reply_type == 3 or reply_type == 4 or reply_type == 5:
		message = "I don't spam. IRC Only"
		sendmsg(message, name, reply_type)
	else:
		message = "--Current Targets--"
		sendmsg(message, name, 2)
		
		for track_target in tracker_target_list:
			sendmsg(track_target, name, 2)	
			
		message = "-----End of List-----"
		sendmsg(message, name, 2)
	
	
#Track Function 
def cmd_track(message, name, reply_type, msg_channel):
	if len(message) > 7:
		track_target = message.split(' ', 1)[1]
		if track_target.find(' ') != -1:
			message = "Could not initialize. Correct usage: " + activator + "track [keyword / username]"
		else:
			if trackers == 0:
				current_date_time = datetime.datetime.now()
				message = "[\x02TRACKER ACTIVATED\x02]: \x02Target:\x02 '" + track_target + "' \x02Date:\x02 '" + current_date_time.strftime("%Y-%m-%d") + "' \x02Time\x02 '" + current_date_time.strftime("%H:%M") + "'"
				track(track_target)
			else:
				message = "Currently only " + str(max_trackers) + " target(s) can be tracked at a time, please untrack first. View current target(s) with " + activator + "trackers"
			
	else:
		message = "Could not initialize. Correct usage: " + activator + "track [keyword / username]"
	
	if reply_type == 3:
		reply_type = 5
	sendmsg(message, name, reply_type, msg_channel)
	

#Untrack Function
def cmd_untrack(message, name, reply_type, msg_channel):
	if len(message) > 9:
		target = message.split(' ', 1)[1]
		if target.find(' ') != -1:
			message = "Correct usage: " + activator + "untrack [keyword / username]"
		else:
			untrack(target)
			message = "Tracker Removed (" + target + ")"
	else:
		message = "Correct usage: " + activator + "untrack [keyword / username]"
		
	if reply_type == 3:
		reply_type = 5
	sendmsg(message, name, reply_type, msg_channel)
	
#Lists all Commands
def cmd_cmds(name, reply_type):
	if reply_type == 3 or reply_type == 4 or reply_type == 5:
		sendmsg("I don't spam, IRC only to view commands", name, reply_type)
		return
	else:
		reply_type = 2
		if is_admin(name):
			sendmsg("Alfred \x02v1.0\x02 Commands \x02[ADMIN]\x02 | Created By Bruce_Bond | Changelog: https://github.com/David-SKB/ProjectButler/blob/master/Changelog.md", name, reply_type)
			sendmsg("---------------------------------------------------------------------------------------------------------------", name, reply_type)
			sendmsg("Note: commands that return values are mostly sent to the location they were triggered, either PM or IRC channel", name, reply_type)
			sendmsg("---------------------------------------------------------------------------------------------------------------", name, reply_type)
			sendmsg(activator + "suptime - VPS server uptime", name, reply_type)
			sendmsg(activator + "uptime - Alfred's current uptime", name, reply_type)
			sendmsg(activator + "joinchan [#channel]", name, reply_type)
			sendmsg(activator + "leavechan [#channel]", name, reply_type)
			sendmsg(activator + "tell [target] [message]", name, reply_type)
			sendmsg(activator + "track [username] - track player messages (Logs to #batcave only. Same password)", name, reply_type)
			sendmsg(activator + "untrack [username] - stop tracking player", name, reply_type)
			sendmsg(activator + "trackers - view tracked targets", name, reply_type)
			sendmsg(activator + "stopwatch - start / stop stopwatch", name, reply_type)
			sendmsg(activator + "timer [seconds] - Starts timer for specified time. Cancel with ?stoptimer", name, reply_type)
		else:
			sendmsg("\x02Alfred \x02v1.0\x02 Commands \x02[USER]\x02 | Created By Bruce_Bond\x02", name, reply_type)
			sendmsg("---------------------------------------------------------------------------------------------------------------", name, reply_type)
			sendmsg("Note: commands that return values are mostly sent to the location they were triggered, either PM or IRC channel", name, reply_type)
			sendmsg("---------------------------------------------------------------------------------------------------------------", name, reply_type)
			sendmsg(activator + "uptime - Alfred's current uptime", name, reply_type)
			sendmsg(activator + "stopwatch - start / stop stopwatch", name, reply_type)
			sendmsg(activator + "timer [seconds] - Starts timer for specified time. Cancel with ?stoptimer", name, reply_type)
			#sendmsg(activator + "", name, reply_type)
			#sendmsg(activator + "", name, reply_type)
			#sendmsg(activator + "", name, reply_type)
			#sendmsg(activator + "", name, reply_type)

#Restarts Alfred
def cmd_restart(name, reply_type, msg_channel):
	if reply_type == 3:
		reply_type = 5
	sendmsg("Restarting...", name, reply_type, msg_channel)
	try:
		cmd_quit(msg_channel, name, reply_type, 0)
	except:
		pass # Ignore when timeout
	time.sleep(2)
	os.execv(sys.executable, ['python'] + sys.argv)
			
			
#Hard quit program and disconnect from server
def cmd_quit(msg_channel, name, reply_type, quit_type):
	if quit_type == 1:
		sendmsg("Until next time sir.", name, reply_type, msg_channel)
	#close any files and stuff here
	time.sleep(2)
	ircsock.send(bytes("QUIT \n"))
	global in_session
	in_session = False
	
main()