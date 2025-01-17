from flask import session
import os
import datetime
import random
import requests
from string import printable
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import pymongo
import smtplib
import ssl
import dns
from bson.objectid import ObjectId
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from html import escape as esc
from lists import shopitems, buffs

clientm = pymongo.MongoClient(os.getenv("clientm"))
usersdb = clientm.Users
profilescol = usersdb.Profiles
notifscol = usersdb.Notifications
gamblingcol = usersdb.Gambling
xpstatscol = usersdb.XPStats
verificationcol = usersdb.Verification
itemscol = usersdb.Items
settingscol = usersdb.Settings
battlecol = usersdb.Battle

with open("static/words.txt", "r") as file:
  allText = file.read()
  words = list(map(str, allText.split()))

def send_mail(usermail, username, id):  
  context = ssl.create_default_context()
  MAILPASS = os.getenv("MAIL_PASSWORD")
  html = f"""
  <h1>Hello {username}!</h1>
  <p><strong>You have signed up for an account / or changed your email in Jasonism!</strong></p>
  <p>Click <a href='https://jasonism.vulcanwm.repl.co/verify/{username}/{str(id)}'>here</a> to verify your account</p>
  <p>Click <a href='https://jasonism-fork.vulcanwm.repl.co/verify/{username}/{str(id)}'>here</a> to verify your account</p>
  <p>If you didn't make this account, reply back to this email saying this isn't your account and <strong>DO NOT</strong> click on the link or the user who made the account will get verified with your email!</p>
  """
  message = MIMEMultipart("alternative")
  message["Subject"] = "Jasonism Verification Email"
  part2 = MIMEText(html, "html")
  message.attach(part2)
  try:
    sendermail = "stanjasonism@gmail.com"
    password = MAILPASS
    gmail_server = smtplib.SMTP('smtp.gmail.com', 587)
    gmail_server.starttls(context=context)
    gmail_server.login(sendermail, password)
    message["From"] = sendermail
    message["To"] = usermail
    gmail_server.sendmail(sendermail, usermail, message.as_string())
    return True
  except Exception as e:
    return "Verification email not sent, due to some issues."
    gmail_server.quit()

def addcookie(key, value):
  session[key] = value

def delcookies():
  session.clear()

def getcookie(key):
  try:
    if (x := session.get(key)):
      return x
    else:
      return False
  except:
    return False

def checkverification(theid):
  myquery = {"_id": ObjectId(theid)}
  mydoc = verificationcol.find(myquery)
  for x in mydoc:
    return x
  return False

def gethashpass(username):
  myquery = { "Username": username }
  mydoc = profilescol.find(myquery)
  for x in mydoc:
    return x['Password']
  return False

def getuserid(id):
  myquery = { "_id": int(id) }
  mydoc = profilescol.find(myquery)
  for x in mydoc:
    return True
  return False

def getuser(username):
  myquery = { "Username": username }
  mydoc = profilescol.find(myquery)
  for x in mydoc:
    if x.get("Deleted", None) == None:
      return x
    return False
  return False

def checkusernamealready(username):
  myquery = { "Username": username }
  mydoc = profilescol.find(myquery)
  for x in mydoc:
    return True
  return False

def checkemailalready(email):
  myquery = { "Email": email }
  mydoc = profilescol.find(myquery)
  for x in mydoc:
    return True
  return False

def checkgambling(username):
  myquery = { "Username": username }
  mydoc = gamblingcol.find(myquery)
  for x in mydoc:
    return x
  document = {
    "Username": username,
    "Flipcoin": [0,0,0,0],
    "Rolldice": [0,0,0,0],
    "Cupgame": [0,0,0,0],
    "RPS": [0,0,0,0,0],
    "ChallengeRPS": [0,0,0,0,0]
  }
  return document

def checkgamblingadd(username):
  myquery = { "Username": username }
  mydoc = gamblingcol.find(myquery)
  for x in mydoc:
    return x
  return False

def addgambling(username, gametype, stats):
  if checkgamblingadd(username) == False:
    document = [{
      "Username": username,
      # [wontime, losttime, wonmoney-lostmoney, howmuchgamble]
      "Flipcoin": [0,0,0,0],
      # [wontime, losttime, wonmoney-lostmoney, howmuchgamble]
      "Rolldice": [0,0,0,0],
      # [wontime, losttime, wonmoney-lostmoney, howmuchgamble]
      "Cupgame": [0,0,0,0],
      # [wontime, losttime, drawtime, wonmoney-lostmoney, howmuchgamble]
      "RPS": [0,0,0,0,0],
      # [wontime, losttime, drawtime, wonmoney-lostmoney, howmuchgamble]
      "ChallengeRPS": [0,0,0,0,0]
    }]
    gamblingcol.insert_many([document])
  userstats = checkgambling(username)
  if gametype == "flipcoin":
    doc = userstats['Flipcoin']
    new0 = stats[0] + doc[0]
    new1 = stats[1] + doc[1]
    new2 = stats[2] + doc[2]
    new3 = stats[3] + doc[3]
    newdoc = [new0, new1, new2, new3]
    del userstats['Flipcoin']
    userstats['Flipcoin'] = newdoc
  if gametype == "rolldice":
    doc = userstats['Rolldice']
    new0 = stats[0] + doc[0]
    new1 = stats[1] + doc[1]
    new2 = stats[2] + doc[2]
    new3 = stats[3] + doc[3]
    newdoc = [new0, new1, new2, new3]
    del userstats['Rolldice']
    userstats['Rolldice'] = newdoc
  if gametype == "cupgame":
    doc = userstats['Cupgame']
    new0 = stats[0] + doc[0]
    new1 = stats[1] + doc[1]
    new2 = stats[2] + doc[2]
    new3 = stats[3] + doc[3]
    newdoc = [new0, new1, new2, new3]
    del userstats['Cupgame']
    userstats['Cupgame'] = newdoc
  if gametype == "rps":
    doc = userstats['RPS']
    new0 = stats[0] + doc[0]
    new1 = stats[1] + doc[1]
    new2 = stats[2] + doc[2]
    new3 = stats[3] + doc[3]
    new4 = stats[4] + doc[4]
    newdoc = [new0, new1, new2, new3, new4]
    del userstats['RPS']
    userstats['RPS'] = newdoc
  if gametype == "challengerps":
    doc = userstats['ChallengeRPS']
    new0 = stats[0] + doc[0]
    new1 = stats[1] + doc[1]
    new2 = stats[2] + doc[2]
    new3 = stats[3] + doc[3]
    new4 = stats[4] + doc[4]
    newdoc = [new0, new1, new2, new3, new4]
    del userstats['ChallengeRPS']
    userstats['ChallengeRPS'] = newdoc
  gamblingcol.delete_one({"Username": username})
  gamblingcol.insert_many([userstats])

def checkxpstats(username):
  myquery = { "Username": username }
  mydoc = xpstatscol.find(myquery)
  for x in mydoc:
    return x
  document = {
    "Username": username,
    # [times won, times lost, xp earned]
    "MenCalc": [0,0,0],
    # [times won, times lost, xp earned]
    "Trivia": [0,0,0],
    # [times won, times lost, xp earned]
    "Unscramble": [0,0,0]
  }
  return document

def addxpstats(username, gametype, stats):
  if checkxpstats(username) == False:
    document = [{
    "Username": username,
    # [times won, times lost, money earned]
    "MenCalc": [0,0,0],
    # [times won, times lost, money earned]
    "Trivia": [0,0,0],
    # [times won, times lost, money earned]
    "Unscramble": [0,0,0]
    }]
    xpstatscol.insert_many(document)
  userstats = checkxpstats(username)
  if gametype == "mencalc":
    doc = userstats['MenCalc']
    new0 = stats[0] + doc[0]
    new1 = stats[1] + doc[1]
    new2 = stats[2] + doc[2]
    newdoc = [new0, new1, new2]
    del userstats['MenCalc']
    userstats['MenCalc'] = newdoc
  if gametype == "trivia":
    doc = userstats['Trivia']
    new0 = stats[0] + doc[0]
    new1 = stats[1] + doc[1]
    new2 = stats[2] + doc[2]
    newdoc = [new0, new1, new2]
    del userstats['Trivia']
    userstats['Trivia'] = newdoc
  if gametype == "unscramble":
    doc = userstats['Unscramble']
    new0 = stats[0] + doc[0]
    new1 = stats[1] + doc[1]
    new2 = stats[2] + doc[2]
    newdoc = [new0, new1, new2]
    del userstats['Unscramble']
    userstats['Unscramble'] = newdoc
  xpstatscol.delete_one({"Username": username})
  xpstatscol.insert_many([userstats])

def makeaccount(username, password, passwordagain):
  if len(username) > 25:
    return "Your username cannot have more than 25 letters!"
  if len(username) < 2:
    return "You have to have more than 2 letters in your username!"
  if set(username).difference(printable) or esc(username) != username:
    return "Your username cannot contain any special characters!"
  if username != username.lower():
    return "Your username has to be all lowercase!"
  if checkusernamealready(username) == True:
    return "A user already has this username! Try another one."
  if password != passwordagain:
    return "The two passwords don't match!"
  if len(password) > 25:
    return "Your password cannot have more than 25 letters!"
  if len(password) < 2:
    return "You have to have more than 2 letters in your password!"
  if set(password).difference(printable):
    return "Your password cannot contain any special characters!"
  passhash = generate_password_hash(password)
  document = [{
    "Username": username,
    "Password": passhash,
    "Created": str(datetime.datetime.now()),
    "Money": 0,
    "XP": 0,
    "Daily": [],
    "Description": None,
    "Verified": False
  }]
  profilescol.insert_many(document)
  return True

def addmoney(username, amount):
  user = getuser(username)
  money = user['Money']
  newmoney = money + amount
  user2 = user
  del user2['Money']
  user2['Money'] = newmoney
  profilescol.delete_one({"Username": username})
  profilescol.insert_many([user2])
  return True

def addxp(username, amount):
  user = getuser(username)
  xp = user['XP']
  newxp = xp + amount
  user2 = user
  del user2['XP']
  user2['XP'] = newxp
  profilescol.delete_one({"Username": username})
  profilescol.insert_many([user2])
  return True

def rps(username, guess, bet):
  try:
    bet = int(bet)
  except:
    return f"{bet} isn't an integer!"
  if bet < 100:
    return "You have to bet at least ∆100!"
  if bet > 10000:
    return "You cannot bet more than ∆10000!"
  comp = random.choice(['rock', 'paper', 'scissors'])
  if comp == 'rock':
    if guess == 'rock':
      addgambling(username, "rps", [0, 0, 1, 0, bet])
      return "It was a draw! You did rock and the computer did rock!"
    if guess == 'paper':
      addgambling(username, "rps", [1, 0, 0, bet*2, bet])
      addmoney(username, bet*2)
      return "You won! You did paper and the computer did rock!"
    if guess == 'scissors':
      addgambling(username, "rps", [0, 1, 0, -1*bet, bet])
      addmoney(username, bet*-1)
      return "You lost! You did scissors and computer did rock!"
  if comp == 'paper':
    if guess == 'rock':
      addgambling(username, "rps", [0, 1, 0, -1*bet, bet])
      addmoney(username, bet*-1)
      return "You lost! You did rock and the computer did paper!"
    if guess == 'paper':
      addgambling(username, "rps", [0, 0, 1, 0, bet])
      return "It was a draw! You did paper and the computer did paper!"
    if guess == 'scissors':
      addgambling(username, "rps", [1, 0, 0, bet*2, bet])
      addmoney(username, bet*2)
      return "You won! You did scissors and the computer did paper!"
  if comp == 'scissors':
    if guess == 'rock':
      addgambling(username, "rps", [1, 0, 0, bet*2, bet])
      addmoney(username, bet*2)
      return "You won! You did rock and the computer did scissors!"
    if guess == 'paper':
      addgambling(username, "rps", [0, 1, 0, -1*bet, bet])
      addmoney(username, bet*-1)
      return "You lost! You did paper and the computer did rock!"
    if guess == 'scissors':
      addgambling(username, "rps", [0, 0, 1, 0, bet])
      return "It was a draw! You did scissors and the computer did scissors!"

def addxpmoney(username, addxp, addmoney):
  user = getuser(username)
  money = user['Money']
  newmoney = money + addmoney
  user2 = user
  del user2['Money']
  user2['Money'] = newmoney
  xp = user['XP']
  newxp = xp + addxp
  del user2['XP']
  user2['XP'] = newxp
  profilescol.delete_one({"Username": username})
  profilescol.insert_many([user2])
  return True

def cupgame(username, guess, bet):
  try:
    bet = int(bet)
  except:
    return f"{bet} isn't an integer!"
  if bet < 100:
    return "You have to bet at least ∆100!"
  if bet > 10000:
    return "You cannot bet more than ∆10000!"
  answer = random.choice(['1', '2', '3'])
  if guess == answer:
    addgambling(username, "cupgame", [1,0,bet*3, bet])
    addmoney(username, bet*3)
    return f"You won! The ball landed in cup {answer}!"
  else:
    addgambling(username, "cupgame", [0,1,bet*-1, bet])
    addmoney(username, bet*-1)
    return f"You lost! The ball landed in cup {answer} and you wanted it to land in cup {guess}!"
  
def rolldice(username, guess, bet):
  try:
    bet = int(bet)
  except:
    return f"{bet} isn't an integer!"
  if bet < 100:
    return "You have to bet at least ∆100!"
  if bet > 10000:
    return "You cannot bet more than ∆10000!"
  answer = random.choice(['1', '2', '3', '4', '5', '6'])
  if guess == answer:
    addgambling(username, "rolldice", [1,0,bet*6, bet])
    addmoney(username, bet*6)
    return f"You won! The dice rolled {answer}!"
  else:
    addgambling(username, "rolldice", [0,1,bet*-1, bet])
    addmoney(username, bet*-1)
    return f"You lost! The dice rolled {answer} and you wanted it to roll {guess}!"

def flipcoin(username, guess, bet):
  try:
    bet = int(bet)
  except:
    return f"{bet} isn't an integer!"
  if bet < 100:
    return "You have to bet at least ∆100!"
  if bet > 10000:
    return "You cannot bet more than ∆10000!"
  answer = random.choice(['heads', 'tails'])
  if guess == answer:
    addgambling(username, "flipcoin", [1,0,bet*2, bet])
    addmoney(username, bet*2)
    return f"You won! The coin flipped {answer}!"
  else:
    addgambling(username, "flipcoin", [0,1,bet*-1, bet])
    addmoney(username, bet*-1)
    return f"You lost! The coin flipped {answer} and you wanted it to flip {guess}!"

def getquestion():
  url = "https://opentdb.com/api.php?amount=1"
  response = requests.get(url)
  return response.json()

def mencalc():
  thetype = random.choice(['add', 'subtract', 'multiply', 'divide', 'square', 'square root'])
  if thetype == 'add':
    number1 = random.randint(100,9999)
    number2 = random.randint(100,9999)
    answer = number1 + number2
    question = f"What is {str(number1)} + {str(number2)}?"
    username = getcookie("User")
    delcookies()
    addcookie("User", username)
    addcookie("MathsAns", str(answer))
    return question
  if thetype == 'subtract':
    number1 = random.randint(100,9999)
    number2 = random.randint(100,9999)
    answer = number1 - number2
    question = f"What is {str(number1)} - {str(number2)}?"
    username = getcookie("User")
    delcookies()
    addcookie("User", username)
    addcookie("MathsAns", str(answer))
    return question
  if thetype == 'multiply':
    number1 = random.randint(0,20)
    number2 = random.randint(0,20)
    answer = number1 * number2
    question = f"What is {str(number1)} × {str(number2)}?"
    username = getcookie("User")
    delcookies()
    addcookie("User", username)
    addcookie("MathsAns", str(answer))
    return question
  if thetype == 'divide':
    answer = random.randint(0,20)
    number2 = random.randint(0,20)
    number1 = number2 * answer
    question = f"What is {str(number1)} ÷ {str(number2)}?"
    username = getcookie("User")
    delcookies()
    addcookie("User", username)
    addcookie("MathsAns", str(answer))
    return question
  if thetype == 'square':
    number = random.randint(0,20)
    answer = number * number
    question = f"What is the square of {str(number)}?"
    username = getcookie("User")
    delcookies()
    addcookie("User", username)
    addcookie("MathsAns", str(answer))
    return question
  if thetype == 'square root':
    answer = random.randint(0,20)
    number = answer * answer
    question = f"What is the square root of {str(number)}?"
    username = getcookie("User")
    delcookies()
    addcookie("User", username)
    addcookie("MathsAns", str(answer))
    return question

def randomword():
  word = random.choice(words)
  return word

def shuffleword(word):
  word = list(word)
  random.shuffle(word)
  shuffle = ''.join(word)
  return shuffle

def getnotifs(username):
  myquery = { "Username": username }
  mydoc = notifscol.find(myquery)
  notifs = []
  for x in mydoc:
    notifs.append(x)
  notifs.reverse()
  return notifs

def getnotifsnotseen(username):
  myquery = { "Username": username }
  mydoc = notifscol.find(myquery)
  notifs = []
  for x in mydoc:
    if x['Seen'] == False:
      notifs.append(x)
  notifs.reverse()
  return notifs

def addnotif(username, notif, typename):
  if isinstance(typename, dict):
    if typename['Type'] == 'RPS':
      notifdoc = {"Username": username, "Seen": False, "Type": "RPS", "Symbol": typename['Symbol'], "Bet": typename['Bet'], "User": typename['User']}
    if typename['Type'] == "Battle":
      notifdoc = {"Username": username, "Seen": False, "Type": "Battle", "Bet": typename['Bet'], "User": typename['User']}
    if typename['Type'] == "BattleGif":
      notifdoc = {"Username": username, "Seen": False, "Type": "BattleGif", "Bet": typename['Bet'], "Winner": typename['Winner'], "Message": typename['Message']}
  else:
    notifdoc = {"Username": username, "Notification": notif, "Seen": False, "Type": "Normal"}
  notifscol.insert_many([notifdoc])
  if isinstance(typename, dict):
    if typename['Type'] == "RPS":
      emailnotif = f"{notifdoc['User']} challenged you to a {notifdoc['Type']} game for ∆{notifdoc['Bet']}!"
    if typename['Type'] == "Battle":
      emailnotif = f"{notifdoc['User']} challenged you to a {notifdoc['Type']} for ∆{notifdoc['Bet']}!"
    if typename['Type'] == "BattleGif":
      emailnotif = typename['Message']
  else:
    emailnotif = notif
  usermail = getuser(username).get("Email", False)
  if usermail == False:
    pass
  else:
    context = ssl.create_default_context()
    MAILPASS = os.getenv("MAIL_PASSWORD")
    html = f"""
    <h1>Hello {username}!</h1>
    <p><strong>New Notification!</strong></p>
    <p>{emailnotif}</p>
    """
    message = MIMEMultipart("alternative")
    message["Subject"] = "Jasonism Email Notification"
    part2 = MIMEText(html, "html")
    message.attach(part2)
    sendermail = "stanjasonism@gmail.com"
    password = MAILPASS
    gmail_server = smtplib.SMTP('smtp.gmail.com', 587)
    gmail_server.starttls(context=context)
    gmail_server.login(sendermail, password)
    message["From"] = sendermail
    message["To"] = usermail
    gmail_server.sendmail(sendermail, usermail, message.as_string())

def clearnotifs(username):
  notifs = getnotifs(username)
  for notif in notifs:
    delete = {"_id": notif['_id']}
    notifscol.delete_one(delete)
  return True

def allseen(username):
  notifs = getnotifs(username)
  myquery = { "Username": username }
  newvalues = { "$set": { "Seen": True } }
  notifscol.update_many(myquery, newvalues)
  return True

def challengerps(username, enemy, bet, symbol):
  try:
    bet = int(bet)
    if getuser(enemy) == False:
      return f"{enemy} is not a real user!"
    if enemy == username:
      return "You cannot challenge yourself!"
    if bet > getuser(enemy)['Money']:
      return f"{enemy} does not have {str(bet)}!"
    if bet > getuser(username)['Money']:
      return f"You don't have {str(bet)}!"
    if getsettings(username)['Passive'] == True:
      return "You are in passive mode so you can't interact with any users!"
    if getsettings(enemy)['Passive'] == True:
      return f"{enemy} is in passive mode so they can't interact with any users!"
    thedict = {"Type": "RPS", "Symbol": symbol, "Bet": bet, "User": username}
    addnotif(enemy, None, thedict)
    addnotif(username, f"You challenged {enemy} to a RPS game for ∆{str(bet)}!", "Normal")
    return True
  except:
    return f"{bet} is not a number!"

def getchallenge(theid):
  mydoc = notifscol.find({"_id": ObjectId(theid)})
  if mydoc == None or mydoc == False or mydoc == []:
    return False
  thedoc = []
  for x in mydoc:
    thedoc.append(x)
  challengedoc = thedoc[0]
  return challengedoc

def denychallenge(username, theid):
  challengedoc = getchallenge(theid)
  if challengedoc == False:
    return "That is not a real challenge!"
  if challengedoc['Username'] != username:
    return "You cannot deny this challenge as it has not been directed to you!"
  if challengedoc['Type'] == "RPS":
    challengesender = challengedoc['User']
    addnotif(username, f"You rejected {challengesender}'s challenge to a {challengedoc['Type']} game for ∆{str(challengedoc['Bet'])}!", "Normal")
    addnotif(challengesender, f"{username} rejected your challenged to a {challengedoc['Type']} game for ∆{str(challengedoc['Bet'])}!", "Normal")
    notifscol.delete_one({"_id": ObjectId(theid)})
    return True
  if challengedoc['Type'] == "Battle":
    challengesender = challengedoc['User']
    addnotif(username, f"You rejected {challengesender}'s challenge to a battle for ∆{str(challengedoc['Bet'])}!", "Normal")
    addnotif(challengesender, f"{username} rejected your challenged to a battle for ∆{str(challengedoc['Bet'])}!", "Normal")
    notifscol.delete_one({"_id": ObjectId(theid)})
    return True

def acceptchallengefuncfunc(user2symbol, user1symbol, user2, user1, bet, theid):
  if user2symbol == 'rock':
    if user1symbol == 'rock':
      addgambling(user1, "challengerps", [0,0,1,0,bet])
      addgambling(user2, "challengerps", [0,0,1,0,bet])
      addnotif(user1, f"The RPS game between you and {user2} was a draw! You didn't win or lose anything!", "Normal")
      addnotif(user2, f"The RPS game between you and {user1} was a draw! You didn't win or lose anything!", "Normal")
    if user1symbol == 'paper':
      addgambling(user1, "challengerps", [1,0,0,bet,bet])
      addgambling(user2, "challengerps", [0,1,0,bet*-1,bet])
      addmoney(user1, bet)
      addmoney(user2, bet*-1)
      addnotif(user1, f"You won the RPS game between you and {user2}! You won ∆{str(bet)}!", "Normal")
      addnotif(user2, f"You lost the RPS game between you and {user1}! You lost ∆{str(bet)}!", "Normal")
    if user1symbol == 'scissors':
      addgambling(user1, "challengerps", [0,1,0,bet*-1,bet])
      addgambling(user2, "challengerps", [1,0,0,bet,bet])
      addmoney(user1, bet*-1)
      addmoney(user2, bet)
      addnotif(user1, f"You lost the RPS game between you and {user2}! You lost ∆{str(bet)}!", "Normal")
      addnotif(user2, f"You won the RPS game between you and {user1}! You won ∆{str(bet)}!", "Normal")
  if user2symbol == 'paper':
    if user1symbol == 'rock':
      addgambling(user1, "challengerps", [0,1,0,bet*-1,bet])
      addgambling(user2, "challengerps", [1,0,0,bet,bet])
      addmoney(user1, bet*-1)
      addmoney(user2, bet)
      addnotif(user1, f"You lost the RPS game between you and {user2}! You lost ∆{str(bet)}!", "Normal")
      addnotif(user2, f"You won the RPS game between you and {user1}! You won ∆{str(bet)}!", "Normal")
    if user1symbol == 'paper':
      addgambling(user1, "challengerps", [0,0,1,0,bet])
      addgambling(user2, "challengerps", [0,0,1,0,bet])
      addnotif(user1, f"The RPS game between you and {user2} was a draw! You didn't win or lose anything!", "Normal")
      addnotif(user2, f"The RPS game between you and {user1} was a draw! You didn't win or lose anything!", "Normal")
    if user1symbol == 'scissors':
      addgambling(user1, "challengerps", [1,0,0,bet,bet])
      addgambling(user2, "challengerps", [0,1,0,bet*-1,bet])
      addmoney(user1, bet)
      addmoney(user2, bet*-1)
      addnotif(user1, f"You won the RPS game between you and {user2}! You won ∆{str(bet)}!", "Normal")
      addnotif(user2, f"You lost the RPS game between you and {user1}! You lost ∆{str(bet)}!", "Normal")
  if user2symbol == 'scissors':
    if user1symbol == 'rock':
      addgambling(user1, "challengerps", [1,0,0,bet,bet])
      addgambling(user2, "challengerps", [0,1,0,bet*-1,bet])
      addmoney(user1, bet)
      addmoney(user2, bet*-1)
      addnotif(user1, f"You won the RPS game between you and {user2}! You won ∆{str(bet)}!", "Normal")
      addnotif(user2, f"You lost the RPS game between you and {user1}! You lost ∆{str(bet)}!", "Normal")
    if user1symbol == 'paper':
      addgambling(user1, "challengerps", [0,1,0,bet*-1,bet])
      addgambling(user2, "challengerps", [1,0,0,bet,bet])
      addmoney(user1, bet*-1)
      addmoney(user2, bet)
      addnotif(user1, f"You lost the RPS game between you and {user2}! You lost ∆{str(bet)}!", "Normal")
      addnotif(user2, f"You won the RPS game between you and {user1}! You won ∆{str(bet)}!", "Normal")
    if user1symbol == 'scissors':
      addgambling(user1, "challengerps", [0,0,1,0,bet])
      addgambling(user2, "challengerps", [0,0,1,0,bet])
      addnotif(user1, f"The RPS game between you and {user2} was a draw! You didn't win or lose anything!", "Normal")
      addnotif(user2, f"The RPS game between you and {user1} was a draw! You didn't win or lose anything!", "Normal")
  notifscol.delete_one({"_id": ObjectId(theid)})

def changeblockname(username, newname):
  user = getuser(username)
  if len(newname) > 15:
    return "Your pet block's name cannot be more than 16 letters long!"
  if set(newname).difference(printable):
    return "Your pet block's name cannot include any special letters!"
  del user['BlockName']
  user['BlockName'] = newname
  profilescol.delete_one({"Username": username})
  profilescol.insert_many([user])
  addlog(f"{username} changed their block name to {newname}")
  return True

def changedesc(username, desc):
  user = getuser(username)
  if len(desc) > 159:
    return "Your description cannot be more than 160 letters long!"
  if set(desc).difference(printable):
    return "Your description cannot include any special letters!"
  del user['Description']
  user['Description'] = desc
  profilescol.delete_one({"Username": username})
  profilescol.insert_many([user])
  addlog(f"{username} changed their description")
  return True

def addlog(log):
  file_object = open('.log', 'a')
  x = str(datetime.datetime.now())
  file_object.write(f'{x}: {log}\n')
  file_object.close()

def changeemail(username, email):
  user = getuser(username)
  emailold = user.get("Email", None)
  if emailold == email:
    return True
  if checkemailalready(email) == True:
    return "This email is already being used by someone else!"
  if emailold != None:
    del user['Email']
  user['Email'] = email
  if user.get("Verified", False) != False:
    del user['Verified']
  user['Verified'] = False
  profilescol.delete_one({"Username": username})
  profilescol.insert_many([user])
  document = {
    "Username": username
  }
  theid = verificationcol.insert(document)
  func = send_mail(email, username, str(theid))
  if func == True:
    return True
  else:
    return func


def verify(username, theid):
  myquery = {"_id": ObjectId(theid)}
  mydoc = verificationcol.find(myquery)
  for x in mydoc:
    if x['Username'] == username:
      verificationcol.delete_one({"_id": x['_id']})
      user = getuser(username)
      del user['Verified']
      user['Verified'] = True
      profilescol.delete_one({"Username": username})
      profilescol.insert_many([user])
      return True
  return False

def getitems(username):
  myquery = {"Username": username}
  mydoc = itemscol.find(myquery)
  for x in mydoc:
    if x.get("Badges", False) == False:
      x['Badges'] = []
    return x
  return {"Username": username, "Items": {}, "Active": [], "Buffs": [], "Badges": []}

def getsettings(username):
  myquery = {"Username": username}
  mydoc = settingscol.find(myquery)
  for x in mydoc:
    return x
  return {"Username": username, "Email": False, "Passive": False}

def changesettings(username, thetype):
  settings = getsettings(username)
  if settings.get("_id", False) != False:
    settingscol.delete_one({"Username": username})
  if thetype == "email":
    if settings['Email'] == False:
      newsetting = True
    if settings['Email'] == True:
      newsetting = False
    del settings['Email']
    settings['Email'] = newsetting
    x = settingscol.insert_many([settings])
    return True
  if thetype == "passive":
    if settings['Passive'] == False:
      if getuser(username)['Money'] < 10000:
        return "You need to have ∆10000 to switch on passive mode!"
      addmoney(username, -10000)
      newsetting = True
    if settings['Passive'] == True:
      newsetting = False
    del settings['Passive']
    settings['Passive'] = newsetting
    settingscol.insert_many([settings])
    return True

def buyitem(username, item, amount):
  item = item.lower()
  amount = int(amount)
  items = shopitems
  useritems = getitems(username)
  if item in items.keys():
    price = items[item] * amount
  elif item in buffs:
    if amount != 1:
      return "You cannot buy more than one of a buff!"
    if useritems['Items'].get(item, 0) != 0:
      return "You cannot buy more than one of a buff!"
    if item in useritems['Buffs']:
      return "You cannot buy more than one of a buff!"
    price = buffs[item]['price'] * amount
  else:
    return "That is not a real item!"
  user = getuser(username)
  if user['Money'] < price:
    return f"You don't have enough money to buy {amount} {item}!"
  useritems = getitems(username)
  itemamount = useritems['Items'].get(item, 0)
  itemamount = itemamount + amount
  if useritems['Items'].get(item, False) != False:
    del useritems['Items'][item]
  useritems['Items'][item] = itemamount
  itemscol.delete_one({"Username": username})
  itemscol.insert_many([useritems])
  addmoney(username, -1 * price)
  return True

def addbuff(buff, username):
  useritems = getitems(username)
  if len(buffs) == 5:
    return "You cannot have more than 5 buffs!"
  if buff in useritems['Buffs']:
    return "You already have this in your buffs!"
  if buff not in useritems['Items']:
    return "You don't own this buff!"
  allbuffs = useritems['Buffs']
  allitems = useritems['Items']
  del allitems[buff]
  allbuffs.append(buff)
  del useritems['Buffs']
  useritems['Buffs'] = allbuffs
  del useritems['Items']
  useritems['Items'] = allitems
  itemscol.delete_one({"Username": username})
  itemscol.insert_many([useritems])
  return True

def additem(username, itemname):
  useritems = getitems(username)
  items = useritems['Items']
  if items.keys().get(itemname, False) != False:
    number = items[itemname]
    del items[itemname]
    items[itemname] = number + 1
  else:
    items[itemname] = 1
  del useritems['Items']
  useritems['Items'] = items
  itemscol.delete_one({"Username": username})
  itemscol.insert_many([useritems])

def removebuff(buff, username):
  useritems = getitems(username)
  if buff not in useritems['Buffs']:
    return "This is not one of your buffs!"
  allbuffs = useritems['Buffs']
  allitems = useritems['Items']
  allbuffs.remove(buff)
  allitems[buff] = 1
  del useritems['Buffs']
  useritems['Buffs'] = allbuffs
  del useritems['Items']
  useritems['Items'] = allitems
  itemscol.delete_one({"Username": username})
  itemscol.insert_many([useritems])
  return True

def battlexp(user1, user2):
  user1items = getitems(user1)
  user2items = getitems(user2)
  user1level = int(str(int(getuser(user1)['XP'])/1000 + 1).split(".")[0])
  user2level = int(str(int(getuser(user2)['XP'])/1000 + 1).split(".")[0])
  user1xp = user1level / 5
  for x in user1items['Buffs']:
    buff = buffs[x]
    xp = buff['battle']
    user1xp = user1xp + xp
  user2xp = user2level / 5
  for x in user2items['Buffs']:
    buff = buffs[x]
    xp = buff['battle']
    user2xp = user2xp + xp
  if user1xp > user2xp:
    return f"{user1} won!"
  elif user2xp > user1xp:
    return f"{user2} won!"
  else:
    number = random.randint(1,2)
    if number == 1:
      return f"{user1} won!"
    else:
      return f"{user2} won!"

def getbattlestats(username):
  myquery = { "Username": username }
  mydoc = battlecol.find(myquery)
  for x in mydoc:
    return x
  document = {
    "Username": username,
    "Count": [0,0],
    # won, lost
    "Money": [0,0]
    # money won, money lost
  }
  return document

def getbattlestatsforadd(username):
  myquery = { "Username": username }
  mydoc = battlecol.find(myquery)
  for x in mydoc:
    return x
  return False

def battle(username, enemy, bet):
  try:
    bet = int(bet)
    if getuser(enemy) == False:
      return f"{enemy} is not a real user!"
    if enemy == username:
      return "You cannot challenge yourself!"
    if bet > getuser(enemy)['Money']:
      return f"{enemy} does not have {str(bet)}!"
    if bet > getuser(username)['Money']:
      return f"You don't have {str(bet)}!"
    if getsettings(username)['Passive'] == True:
      return "You are in passive mode so you can't interact with any users!"
    if getsettings(enemy)['Passive'] == True:
      return f"{enemy} is in passive mode so they can't interact with any users!"
    thedict = {"Type": "Battle", "Bet": bet, "User": username}
    addnotif(enemy, None, thedict)
    addnotif(username, f"You challenged {enemy} to a battle for ∆{str(bet)}!", "Normal")
    return True
  except:
    return f"{bet} is not a number!"

def acceptchallengebattle(challengeid):
  challenge = getchallenge(challengeid)
  bet = challenge['Bet']
  func = battlexp(challenge['Username'], challenge['User'])
  if challenge['Username'] in func:
    addmoney(challenge['Username'], bet)
    addmoney(challenge['User'], bet*-1)
    addxp(challenge['Username'], 250)
    changebattlestats(challenge['Username'], [1,0,bet,0])
    changebattlestats(challenge['User'], [0,1,0,bet])
    thedictuser = {"Type": "BattleGif", "Bet": bet, "Winner": challenge['Username'], "Message": f"You won the battle between you and {challenge['User']}! You won ∆{str(bet)} and 250 XP !"}
    addnotif(challenge['Username'], None, thedictuser)
    thedictuser2 = {"Type": "BattleGif", "Bet": bet, "Winner": challenge['Username'], "Message": f"You lost the RPS game between you and {challenge['Username']}! You lost ∆{str(bet)}!"}
    addnotif(challenge['User'], None, thedictuser2)
  else:
    addmoney(challenge['User'], bet)
    addmoney(challenge['Username'], bet*-1)
    addxp(challenge['User'], 250)
    changebattlestats(challenge['User'], [1,0,bet,0])
    changebattlestats(challenge['Username'], [0,1,0,bet])
    thedictuser = {"Type": "BattleGif", "Bet": bet, "Winner": challenge['User'], "Message": f"You lost the battle between you and {challenge['User']}! You lost ∆{str(bet)}!"}
    addnotif(challenge['Username'], None, thedictuser)
    thedictuser2 = {"Type": "BattleGif", "Bet": bet, "Winner": challenge['User'], "Message": f"You won the RPS game between you and {challenge['Username']}! You won ∆{str(bet)} and 250 XP!"}
    addnotif(challenge['User'], None, thedictuser2)
  notifscol.delete_one({"_id": ObjectId(challengeid)})

def changebattlestats(username, stats):
  if getbattlestatsforadd(username) == False:
    document = {
      "Username": username,
      "Count": [0,0],
      # won, lost
      "Money": [0,0]
      # money won, money lost
    }
    battlecol.insert_many([document])
  userstats = getbattlestats(username)
  countdoc = userstats['Count']
  count0 = stats[0] + countdoc[0]
  count1 = stats[1] + countdoc[1]
  moneydoc = userstats['Money']
  money0 = stats[2] + moneydoc[0]
  money1 = stats[3] + moneydoc[1]
  newcount = [count0, count1]
  newmoney = [money0, money1]
  del userstats['Count']
  userstats['Count'] = newcount
  del userstats['Money']
  userstats['Money'] = newmoney
  battlecol.delete_one({"Username": username})
  battlecol.insert_many([userstats])

def xpleaderboard():
  mydoc = profilescol.find().sort("XP", -1).limit(10)
  lb = []
  for x in mydoc:
    del x['Password']
    lb.append(x)
  return lb

def moneyleaderboard():
  mydoc = profilescol.find().sort("Money", -1).limit(10)
  lb = []
  for x in mydoc:
    del x['Password']
    lb.append(x)
  return lb

def addbadge(username, badgename):
  useritems = getitems(username)
  badges = useritems['Badges']
  badges.append(badgename)
  del useritems['Badges']
  useritems['Badges'] = badges
  itemscol.delete_one({"Username": username})
  itemscol.insert_many([useritems])