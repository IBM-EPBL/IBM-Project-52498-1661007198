from flask import Flask, request,flash, render_template, redirect, url_for, session
import re
import os
import ibm_db
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=824dfd4d-99de-440d-9991-629c01b3832d.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=30119;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=tlf99662;PWD=Xcek6mxqCkEh6uRm", '', '')


app = Flask(__name__)
app.secret_key = 'a'
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/userreg')
def userreg():
    return render_template("userregister.html")

@app.route('/userlog') 
def userlog():
    return render_template("userlogin.html")

@app.route('/userregister', methods = ["POST"])
def userregister():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        sql = "SELECT * FROM users WHERE username =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'username must contain only characters and numbers !'
        else:
            insert_sql = "INSERT INTO users VALUES (?,?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.bind_param(prep_stmt, 4, 0)
            ibm_db.bind_param(prep_stmt, 5, 0)
            ibm_db.bind_param(prep_stmt, 6, 0)
            ibm_db.execute(prep_stmt)
            message = Mail(
                from_email='customer.care.registry.ntp@gmail.com',
                to_emails=email ,
                subject='Customer Care Registry - Account Creation',
                html_content='Hello '+username + ',\n\n'+ """\n\nThank you for registering as a customer with Customer Care Registry Application. """)
                
            sg = SendGridAPIClient('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')
            response = sg.send(message)
            stmt = "SELECT TOTALNOTIFICATIONS FROM ADMIN WHERE ADMINUSERNAME=?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, 'admin12')
            ibm_db.execute(prep_stmt)
            account = ibm_db.fetch_assoc(prep_stmt)
            notifications = (int)(account['TOTALNOTIFICATIONS'])
            notifications += 1
            stmt = "UPDATE ADMIN SET TOTALNOTIFICATIONS = ? WHERE ADMINUSERNAME = ?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, notifications)
            ibm_db.bind_param(prep_stmt, 2, 'admin12')
            ibm_db.execute(prep_stmt)
            stmt = "SELECT NOTIFICATIONS FROM USERS WHERE USERNAME=?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.execute(prep_stmt)
            account = ibm_db.fetch_assoc(prep_stmt)
            notifications = (int)(account['NOTIFICATIONS'])
            notifications += 1
            stmt = "UPDATE USERS SET NOTIFICATIONS = ? WHERE USERNAME = ?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, notifications)
            ibm_db.bind_param(prep_stmt, 2, username)
            ibm_db.execute(prep_stmt)
            stmt = "SELECT USERSCOUNT FROM ADMIN WHERE ADMINUSERNAME=?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, 'admin12')
            ibm_db.execute(prep_stmt)
            account = ibm_db.fetch_assoc(prep_stmt)
            usercount = (int)(account['USERSCOUNT'])
            usercount += 1

            stmt = "UPDATE ADMIN SET USERSCOUNT = ? WHERE ADMINUSERNAME = ?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, usercount)
            ibm_db.bind_param(prep_stmt, 2, 'admin12')
            ibm_db.execute(prep_stmt)

            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template("userregister.html", msg = msg)
@app.route('/userlogin', methods= ["POST"])
def userlogin():
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        sql = "SELECT * FROM users WHERE username =? AND password = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            session['loggedin'] = True
            session['EMAILADDRESS'] = account['EMAILADDRESS']
            session['USERNAME'] = account['USERNAME']
            msg = "Login Successful"
            flash("Login successful")
            return redirect(url_for('userdashboard'))
        else:
            flash("Incorrect username / Password !")
            msg = "Incorrect username / Password !"
            
    return render_template('userlogin.html', msg = msg)
@app.route('/agentreg')
def agentreg():
    return render_template("agentregister.html")

@app.route('/agentlog') 
def agentlog():
    return render_template("agentlogin.html")

@app.route('/agentregister', methods = ["POST"])
def agentregister():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        sql = "SELECT * FROM agents WHERE agentusername =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            msg = 'Agent Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'username must contain only characters and numbers !'
        else:
            insert_sql = "INSERT INTO agents VALUES (?,?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.bind_param(prep_stmt, 4, 0)
            ibm_db.bind_param(prep_stmt, 5, 0)
            ibm_db.bind_param(prep_stmt, 6, 0)
            ibm_db.execute(prep_stmt)
            message = Mail(
                from_email='customer.care.registry.ntp@gmail.com',
                to_emails=email ,
                subject='Customer Care Registry - Agent Account Creation',
                html_content='Hello '+username + ',\n\n'+ """\n\nYou have successfully registered as an agent with Customer Care Registry. You can login and access your dashboard now.""")
                
            sg = SendGridAPIClient('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')
            response = sg.send(message)
            stmt = "SELECT TOTALNOTIFICATIONS FROM ADMIN WHERE ADMINUSERNAME=?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, 'admin12')
            ibm_db.execute(prep_stmt)
            account = ibm_db.fetch_assoc(prep_stmt)
            notifications = (int)(account['TOTALNOTIFICATIONS'])
            notifications += 1
            stmt = "UPDATE ADMIN SET TOTALNOTIFICATIONS = ? WHERE ADMINUSERNAME = ?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, notifications)
            ibm_db.bind_param(prep_stmt, 2, 'admin12')
            ibm_db.execute(prep_stmt)
            stmt = "SELECT NOTIFICATION FROM AGENTS WHERE AGENTUSERNAME=?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.execute(prep_stmt)
            account = ibm_db.fetch_assoc(prep_stmt)
            notifications = (int)(account['NOTIFICATION'])
            notifications += 1
            stmt = "UPDATE AGENTS SET NOTIFICATION = ? WHERE AGENTUSERNAME = ?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, notifications)
            ibm_db.bind_param(prep_stmt, 2, username)
            ibm_db.execute(prep_stmt)
            stmt = "SELECT AGENTSCOUNT FROM ADMIN WHERE ADMINUSERNAME=?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, 'admin12')
            ibm_db.execute(prep_stmt)
            account = ibm_db.fetch_assoc(prep_stmt)
            agentcount = (int)(account['AGENTSCOUNT'])
            agentcount += 1

            stmt = "UPDATE ADMIN SET AGENTSCOUNT = ? WHERE ADMINUSERNAME = ?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, agentcount)
            ibm_db.bind_param(prep_stmt, 2, 'admin12')
            ibm_db.execute(prep_stmt)

            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template("agentregister.html", msg = msg)
@app.route('/agentlogin', methods= ["POST"])
def agentlogin():
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        sql = "SELECT * FROM agents WHERE agentusername =? AND agentpassword = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            session['loggedin'] = True
            session['AGENTEMAILADDRESS'] = account['AGENTEMAILADDRESS']
            session['AGENTUSERNAME'] = account['AGENTUSERNAME']
            flash("Agent Login successful")
            return redirect(url_for('agentdashboard'))
        else:
            flash("Incorrect username / Password !")
        
    return render_template('agentlogin.html')

@app.route('/adminlog') 
def adminlog():
    return render_template("adminlogin.html")

@app.route('/adminlogin', methods= ["POST"])
def adminlogin():
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        sql = "SELECT * FROM admin WHERE adminusername =? AND adminpassword = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            session['loggedin'] = True
            session['ADMINEMAILADDRESS'] = account['ADMINEMAILADDRESS']
            session['ADMINUSERNAME'] = account['ADMINUSERNAME']
            flash("Admin Login successful")
            return redirect(url_for('admindashboard'))
        else:
            flash("Incorrect username / Password !")
        
    return render_template('adminlogin.html')


@app.route('/userdashboard')
def userdashboard():
    if 'loggedin' in session:
        sql = "SELECT TOTALTICKETS FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,'admin12')
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg5 = int(account['TOTALTICKETS'])

        sql = "SELECT TOTALNOTIFICATIONS FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,'admin12')
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg6 = int(account['TOTALNOTIFICATIONS'])

        sql = "SELECT USERSCOUNT FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,'admin12')
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg7 = int(account['USERSCOUNT'])

        sql = "SELECT TICKETSRESOLVED FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,'admin12')
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg8 = int(account['TICKETSRESOLVED'])

        sql = "SELECT TICKETS FROM USERS WHERE USERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['USERNAME'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg11 = int(account['TICKETS'])

        sql = "SELECT TICKETSRESOLVED FROM USERS WHERE USERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['USERNAME'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg33 = int(account['TICKETSRESOLVED'])

        msg22 = msg11 - msg33

        sql = "SELECT NOTIFICATIONS FROM USERS WHERE USERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['USERNAME'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg44 = int(account['NOTIFICATIONS'])
    
        return render_template('userdashboard.html', username=session['USERNAME'], msg5 = msg5, msg6 = msg6, msg7 = msg7, msg8 = msg8, msg11 = msg11, msg22 = msg22, msg33 = msg33, msg44 = msg44)

    return redirect(url_for('userlog'))
@app.route('/raiseticket')
def raiseticket():
    if 'loggedin' in session:
        return render_template("raiseTickets.html", username = session['USERNAME'])
    return redirect(url_for('userlog'))

@app.route('/raiseticketUser', methods = ["POST"])
def raiseticketUser():
    if 'loggedin' in session:
        msg = ''
        if request.method == 'POST' :
            issue = request.form['issue']
            number = (int)(request.form['number'])
            sql = "SELECT TOTALTICKETS FROM ADMIN WHERE ADMINUSERNAME = ?   "
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,'admin12')
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            ticketid = int(account['TOTALTICKETS'])
            ticketid+=1

            insert_sql = "INSERT INTO TICKETS(TICKETID,USERNAME,EMAIL,DESCRIPTION,STATUS,BILLNO) VALUES (?,?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, ticketid)
            ibm_db.bind_param(prep_stmt, 2, session['USERNAME'])
            ibm_db.bind_param(prep_stmt, 3, session['EMAILADDRESS'])
            ibm_db.bind_param(prep_stmt, 4, issue)
            ibm_db.bind_param(prep_stmt, 5, 'Raised')
            ibm_db.bind_param(prep_stmt, 6, number)
            ibm_db.execute(prep_stmt)

            message = Mail(
                from_email='customer.care.registry.ntp@gmail.com',
                to_emails=session['EMAILADDRESS'] ,
                subject='Customer Care Registry - Ticket Raised',
                html_content='Hello '+session['USERNAME'] + ',\n\n'+ """\n\nYou have successfully raised your ticket in Customer Care Registry. Current status of your ticket is 'Raised'. Soon, your ticket will be alloted to an agent by the admin. Thank you for using our application.""")
                
            sg = SendGridAPIClient('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')
            response = sg.send(message)
            stmt = "SELECT TOTALNOTIFICATIONS FROM ADMIN WHERE ADMINUSERNAME=?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, 'admin12')
            ibm_db.execute(prep_stmt)
            account = ibm_db.fetch_assoc(prep_stmt)
            notifications = (int)(account['TOTALNOTIFICATIONS'])
            notifications += 1
            stmt = "UPDATE ADMIN SET TOTALNOTIFICATIONS = ? WHERE ADMINUSERNAME = ?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, notifications)
            ibm_db.bind_param(prep_stmt, 2, 'admin12')
            ibm_db.execute(prep_stmt)
            stmt = "SELECT NOTIFICATIONS FROM USERS WHERE USERNAME=?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, session['USERNAME'])
            ibm_db.execute(prep_stmt)
            account = ibm_db.fetch_assoc(prep_stmt)
            notifications = (int)(account['NOTIFICATIONS'])
            notifications += 1
            stmt = "UPDATE USERS SET NOTIFICATIONS = ? WHERE USERNAME = ?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, notifications)
            ibm_db.bind_param(prep_stmt, 2, session['USERNAME'])
            ibm_db.execute(prep_stmt)

            stmt = "UPDATE ADMIN SET TOTALTICKETS = ? WHERE ADMINUSERNAME = ?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, ticketid)
            ibm_db.bind_param(prep_stmt, 2, 'admin12')
            ibm_db.execute(prep_stmt)

            stmt = "SELECT TICKETS FROM USERS WHERE USERNAME=?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, session['USERNAME'])
            ibm_db.execute(prep_stmt)
            account = ibm_db.fetch_assoc(prep_stmt)
            tickets = (int)(account['TICKETS'])
            tickets += 1

            stmt = "UPDATE USERS SET TICKETS = ? WHERE USERNAME = ?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, tickets)
            ibm_db.bind_param(prep_stmt, 2, session['USERNAME'])
            ibm_db.execute(prep_stmt)
            msg = "Ticket Raised Successfully !!"
        else:
            msg = "Something went wrong. Please try again later"
        return render_template("raiseTickets.html", msg = msg, username= session['USERNAME'])
    return redirect(url_for('userlog'))

@app.route('/userprofile')
def userprofileinfo():
    if 'loggedin' in session:
        msg1 = session['USERNAME']
        msg2 = session["EMAILADDRESS"]
        sql = "SELECT NOTIFICATIONS FROM USERS WHERE USERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['USERNAME'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg3 = int(account['NOTIFICATIONS'])
        sql = "SELECT TICKETS FROM USERS WHERE USERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['USERNAME'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg4 = int(account['TICKETS'])
        msg5 = msg4
        sql = "SELECT TICKETSRESOLVED FROM USERS WHERE USERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['USERNAME'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg7 = int(account['TICKETSRESOLVED'])
        msg6 = msg4 - msg5
        msg8 = msg3
        return render_template('userprofile.html',msg1 = msg1,msg2=msg2,msg3 = msg3, msg4 = msg4,msg5=msg5, msg6=msg6, msg7=msg7, msg8=msg8, username=session['USERNAME'] )
    return redirect(url_for('userlog'))

@app.route('/agentprofile')
def agentprofileinfo():
    if 'loggedin' in session:
        msg1 = session['AGENTUSERNAME']
        msg2 = session["AGENTEMAILADDRESS"]
        sql = "SELECT NOTIFICATION FROM AGENTS WHERE AGENTUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['AGENTUSERNAME'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg3 = int(account['NOTIFICATION'])
        sql = "SELECT AGENTTICKETS FROM AGENTS WHERE AGENTUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['AGENTUSERNAME'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg4 = int(account['AGENTTICKETS'])
        msg5 = msg4
        sql = "SELECT AGENTTICKETSRESOLVED FROM AGENTS WHERE AGENTUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['AGENTUSERNAME'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg7 = int(account['AGENTTICKETSRESOLVED'])
        msg6 = msg4 - msg5
        msg8 = msg3
        return render_template('agentprofile.html',msg1 = msg1,msg2=msg2,msg3 = msg3, msg4 = msg4,msg5=msg5, msg6=msg6, msg7=msg7, msg8=msg8, username=session['AGENTUSERNAME'])
    return redirect(url_for('agentlog'))

@app.route('/adminprofile')
def adminprofileinfo():
    if 'loggedin' in session:
        msg1 = session['ADMINUSERNAME']
        msg2 = session["ADMINEMAILADDRESS"]
        sql = "SELECT AGENTSCOUNT FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['ADMINUSERNAME'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg3 = int(account['AGENTSCOUNT'])
        sql = "SELECT USERSCOUNT FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['ADMINUSERNAME'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg4 = int(account['USERSCOUNT'])
        sql = "SELECT TOTALTICKETS FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['ADMINUSERNAME'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg5 = int(account['TOTALTICKETS'])
        sql = "SELECT TICKETSRESOLVED FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['ADMINUSERNAME'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg7 = int(account['TICKETSRESOLVED'])
        msg6 = msg5 - msg7
        sql = "SELECT TOTALNOTIFICATIONS FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['ADMINUSERNAME'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg8 = int(account['TOTALNOTIFICATIONS'])
        return render_template('adminprofile.html',msg1 = msg1,msg2=msg2,msg3 = msg3, msg4 = msg4,msg5=msg5, msg6=msg6, msg7=msg7, msg8=msg8, username=session['ADMINUSERNAME'])
    return redirect(url_for('adminlog'))


@app.route('/admindashboard')
def admindashboard():
    if 'loggedin' in session:
        sql = "SELECT TOTALTICKETS FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,'admin12')
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg5 = int(account['TOTALTICKETS'])

        sql = "SELECT TOTALNOTIFICATIONS FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,'admin12')
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg6 = int(account['TOTALNOTIFICATIONS'])

        sql = "SELECT USERSCOUNT FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,'admin12')
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg7 = int(account['USERSCOUNT'])

        sql = "SELECT TICKETSRESOLVED FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,'admin12')
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg8 = int(account['TICKETSRESOLVED'])

        sql = "SELECT AGENTSCOUNT FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,'admin12')
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg11 = int(account['AGENTSCOUNT'])

        sql = "SELECT USERSCOUNT FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,'admin12')
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg22 = int(account['USERSCOUNT'])

        sql = "SELECT ASSIGNTICKETS FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,'admin12')
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg33 = int(account['ASSIGNTICKETS'])


        sql = "SELECT TICKETSRESOLVED FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,'admin12')
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg44 = int(account['TICKETSRESOLVED'])
    
        return render_template('admindashboard.html', username=session['ADMINUSERNAME'], msg5 = msg5, msg6 = msg6, msg7 = msg7, msg8 = msg8, msg11 = msg11, msg22 = msg22, msg33 = msg33, msg44 = msg44)

    return redirect(url_for('adminlog'))

@app.route('/viewCustomers')
def viewCustomers():
    if 'loggedin' in session:
        customers = []
        sql = "SELECT USERNAME, EMAILADDRESS, TICKETS, TICKETSRESOLVED, NOTIFICATIONS FROM USERS"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            customers.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
        if customers:
            return render_template("viewCustomersAdmin.html", customers = customers, username = session['ADMINUSERNAME'])
    return redirect(url_for('adminlog'))

@app.route('/viewAllTicketsUser')
def viewAllTicketsUser():
    if 'loggedin' in session:
        tickets = []
        sql = "SELECT TICKETID, DESCRIPTION, BILLNO, AGENTUSERNAME, STATUS FROM TICKETS WHERE USERNAME = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['USERNAME'])
        ibm_db.execute(stmt)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            tickets.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
        if tickets:
            return render_template("viewAllTicketsUser.html", tickets = tickets, username = session['USERNAME'])
    return redirect(url_for('userlog'))

@app.route('/viewAllTicketsInProgress')
def viewAllTicketsInProgressUser():
    if 'loggedin' in session:
        tickets = []
        sql = "SELECT TICKETID, DESCRIPTION, BILLNO, AGENTUSERNAME, STATUS FROM TICKETS WHERE USERNAME = ? AND STATUS = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['USERNAME'])
        ibm_db.bind_param(stmt,2,'In Progress')
        ibm_db.execute(stmt)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            tickets.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
        if tickets:
            return render_template("viewAllTicketsInProgressUser.html", tickets = tickets, username = session['USERNAME'])
    return redirect(url_for('userlog'))

@app.route('/viewAllTicketsResolved')
def viewAllTicketsResolvedUser():
    if 'loggedin' in session:
        tickets = []
        sql = "SELECT TICKETID, DESCRIPTION, BILLNO, AGENTUSERNAME, STATUS FROM TICKETS WHERE USERNAME = ? AND STATUS = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['USERNAME'])
        ibm_db.bind_param(stmt,2,'Ticket Resolved')
        ibm_db.execute(stmt)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            tickets.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
        if tickets:
            return render_template("viewAllTicketsResolvedUser.html", tickets = tickets, username = session['USERNAME'])
    return redirect(url_for('userlog'))

@app.route('/viewTickets')
def viewTickets():
    if 'loggedin' in session:
        tickets = []
        sql = "SELECT TICKETID, USERNAME, EMAIL, DESCRIPTION, BILLNO, STATUS FROM TICKETS WHERE AGENTUSERNAME = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['AGENTUSERNAME'])
        ibm_db.execute(stmt)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            tickets.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
        if tickets:
            return render_template("viewTicketsAgent.html", tickets = tickets, username = session['AGENTUSERNAME'])
    return redirect(url_for('agentlog'))

@app.route('/viewTickets/<name>')
def viewTicketsAgent(name):
    if 'loggedin' in session:
        status = []
        status.append('In Progress')
        status.append('Ticket Resolved')
        if status:
            return render_template("changeTicketStatus.html", status = status, username = session['AGENTUSERNAME'],ticketid=name, msg11 = "In Progress", msg22 = "Ticket Resolved")
    return redirect(url_for('adminlog'))

@app.route('/changeTicketStatus/<ticket>/<status>')
def changeTicketStatus(ticket, status):
    if 'loggedin' in session:
        msg=""
        stmt = "UPDATE TICKETS SET STATUS = ? WHERE TICKETID = ?"
        prep_stmt = ibm_db.prepare(conn, stmt)
        ibm_db.bind_param(prep_stmt, 1, status)
        ibm_db.bind_param(prep_stmt, 2, ticket)
        ibm_db.execute(prep_stmt)
        if status == 'Ticket Resolved':
            sql = "SELECT TICKETSRESOLVED FROM ADMIN WHERE ADMINUSERNAME = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, 'admin12')
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            adminTicketResolved = (int)(account['TICKETSRESOLVED'])
            adminTicketResolved+=1

            sql = "UPDATE ADMIN SET TICKETSRESOLVED = ? WHERE ADMINUSERNAME = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, adminTicketResolved)
            ibm_db.bind_param(stmt, 2, 'admin12')
            ibm_db.execute(stmt)

            sql = "SELECT AGENTTICKETSRESOLVED FROM AGENTS WHERE AGENTUSERNAME = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, session["AGENTUSERNAME"])
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            adminTicketResolved = (int)(account['AGENTTICKETSRESOLVED'])
            adminTicketResolved+=1

            sql = "UPDATE AGENTS SET AGENTTICKETSRESOLVED = ? WHERE AGENTUSERNAME = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, adminTicketResolved)
            ibm_db.bind_param(stmt, 2, session["AGENTUSERNAME"])
            ibm_db.execute(stmt)

            sql = "SELECT USERNAME FROM TICKETS WHERE TICKETID = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, ticket)
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            username = account['USERNAME']
            
            sql = "SELECT TICKETSRESOLVED, EMAILADDRESS FROM USERS WHERE USERNAME = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, username)
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            TicketResolved = (int)(account['TICKETSRESOLVED'])
            TicketResolved+=1
            email = account['EMAILADDRESS']

            sql = "UPDATE USERS SET TICKETSRESOLVED = ? WHERE USERNAME = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, TicketResolved)
            ibm_db.bind_param(stmt, 2, username)
            ibm_db.execute(stmt)

            message = Mail(
                from_email='customer.care.registry.ntp@gmail.com',
                to_emails=email ,
                subject='Customer Care Registry - Ticket Resolved',
                html_content='Hello '+username + ',\n\n'+ """\n\nYour ticket with ticketid. """+ticket+'was resolved. Thank you for using our application.')
                
            sg = SendGridAPIClient('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')
            response = sg.send(message)
            stmt = "SELECT TOTALNOTIFICATIONS FROM ADMIN WHERE ADMINUSERNAME=?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, 'admin12')
            ibm_db.execute(prep_stmt)
            account = ibm_db.fetch_assoc(prep_stmt)
            notifications = (int)(account['TOTALNOTIFICATIONS'])
            notifications += 1
            stmt = "UPDATE ADMIN SET TOTALNOTIFICATIONS = ? WHERE ADMINUSERNAME = ?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, notifications)
            ibm_db.bind_param(prep_stmt, 2, 'admin12')
            ibm_db.execute(prep_stmt)
            stmt = "SELECT NOTIFICATIONS FROM USERS WHERE USERNAME=?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.execute(prep_stmt)
            account = ibm_db.fetch_assoc(prep_stmt)
            notifications = (int)(account['NOTIFICATIONS'])
            notifications += 1
            stmt = "UPDATE USERS SET NOTIFICATIONS = ? WHERE USERNAME = ?"
            prep_stmt = ibm_db.prepare(conn, stmt)
            ibm_db.bind_param(prep_stmt, 1, notifications)
            ibm_db.bind_param(prep_stmt, 2, username)
            ibm_db.execute(prep_stmt)
        return redirect(url_for('viewTickets'))
    return redirect(url_for('agentlog'))
    


@app.route('/assignTickets')
def assignTickets():
    if 'loggedin' in session:
        tickets = []
        sql = "SELECT TICKETID, USERNAME, EMAIL, DESCRIPTION, BILLNO, AGENTUSERNAME, AGENTEMAIL, STATUS FROM TICKETS"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            tickets.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
        if tickets:
            return render_template("assignTicketsAdmin.html", tickets = tickets, username = session['ADMINUSERNAME'])
    return redirect(url_for('adminlog'))




@app.route('/assignTickets/<name>')
def assignTicketsAgentAdmin(name):
    if 'loggedin' in session:
        agents = []
        sql = "SELECT AGENTUSERNAME, AGENTEMAILADDRESS, AGENTTICKETS, AGENTTICKETSRESOLVED FROM AGENTS"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            agents.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
        if agents:
            return render_template("assignAgentAdmin.html", agents = agents, username = session['ADMINUSERNAME'],ticketid=name)
    return redirect(url_for('adminlog'))


#edit this
@app.route('/assignTicketsAdmin/<ticket>/<username>')
def assignTicketsAdmin(ticket, username):
    if 'loggedin' in session:
        msg=""
        stmt = "UPDATE TICKETS SET STATUS = ?, AGENTUSERNAME = ? WHERE TICKETID = ?"
        prep_stmt = ibm_db.prepare(conn, stmt)
        ibm_db.bind_param(prep_stmt, 1, 'Agent Alloted')
        ibm_db.bind_param(prep_stmt, 2, username)
        ibm_db.bind_param(prep_stmt, 3, ticket)
        ibm_db.execute(prep_stmt)

        stmt = "SELECT AGENTTICKETS, AGENTEMAILADDRESS FROM AGENTS WHERE AGENTUSERNAME=?"
        prep_stmt = ibm_db.prepare(conn, stmt)
        ibm_db.bind_param(prep_stmt, 1, username)
        ibm_db.execute(prep_stmt)
        account = ibm_db.fetch_assoc(prep_stmt)
        agentTicket = account['AGENTTICKETS']
        emailaddress = account['AGENTEMAILADDRESS']
        agentTicket+=1

        stmt = "UPDATE AGENTS SET AGENTTICKETS = ? WHERE AGENTUSERNAME = ?"
        prep_stmt = ibm_db.prepare(conn, stmt)
        ibm_db.bind_param(prep_stmt, 1, agentTicket)
        ibm_db.bind_param(prep_stmt, 2, username)
        ibm_db.execute(prep_stmt)

        message = Mail(
                from_email='customer.care.registry.ntp@gmail.com',
                to_emails=emailaddress ,
                subject='Customer Care Registry - Ticket Assigned',
                html_content='Hello '+username + ',\n\n'+ """\n\nYou are assigned with a ticket to resolve by the admin. Log in to your dashboard to know about the ticket and start resolving it.""")
                
        sg = SendGridAPIClient('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')
        response = sg.send(message)

        stmt = "SELECT TOTALNOTIFICATIONS FROM ADMIN WHERE ADMINUSERNAME=?"
        prep_stmt = ibm_db.prepare(conn, stmt)
        ibm_db.bind_param(prep_stmt, 1, 'admin12')
        ibm_db.execute(prep_stmt)
        account = ibm_db.fetch_assoc(prep_stmt)
        notifications = (int)(account['TOTALNOTIFICATIONS'])
        notifications += 1
        stmt = "UPDATE ADMIN SET TOTALNOTIFICATIONS = ? WHERE ADMINUSERNAME = ?"
        prep_stmt = ibm_db.prepare(conn, stmt)
        ibm_db.bind_param(prep_stmt, 1, notifications)
        ibm_db.bind_param(prep_stmt, 2, 'admin12')
        ibm_db.execute(prep_stmt)
        stmt = "SELECT NOTIFICATION FROM AGENTS WHERE AGENTUSERNAME=?"
        prep_stmt = ibm_db.prepare(conn, stmt)
        ibm_db.bind_param(prep_stmt, 1, username)
        ibm_db.execute(prep_stmt)
        account = ibm_db.fetch_assoc(prep_stmt)
        notifications = (int)(account['NOTIFICATION'])
        notifications += 1
        stmt = "UPDATE AGENTS SET NOTIFICATION = ? WHERE AGENTUSERNAME = ?"
        prep_stmt = ibm_db.prepare(conn, stmt)
        ibm_db.bind_param(prep_stmt, 1, notifications)
        ibm_db.bind_param(prep_stmt, 2, username)
        ibm_db.execute(prep_stmt)
            
        agents = []
        sql = "SELECT AGENTUSERNAME FROM AGENTS"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            agents.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
        if agents:
            return redirect(url_for('assignTickets'))
    return redirect(url_for('adminlog'))

@app.route('/deleteCustomers')
def deleteCustomers():
    if 'loggedin' in session:
        customers = []
        sql = "SELECT USERNAME, EMAILADDRESS, TICKETS, TICKETSRESOLVED, NOTIFICATIONS FROM USERS"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            customers.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
        if customers:
            return render_template("deleteCustomersAdmin.html", customers = customers, username = session['ADMINUSERNAME'])
    return redirect(url_for('adminlog'))

@app.route('/deleteCustomers/<name>')
def deleteCustomersName(name):
    if 'loggedin' in session:
        sql = "SELECT * FROM USERS WHERE USERNAME=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,name)
        ibm_db.execute(stmt)
        customer = ibm_db.fetch_row(stmt)
        if customer:
            sql = "DELETE FROM USERS WHERE USERNAME=?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,name)
            ibm_db.execute(stmt)

            sql = "SELECT USERSCOUNT FROM ADMIN WHERE ADMINUSERNAME = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,'admin12')
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            count = int(account['USERSCOUNT'])
            
            sql = "UPDATE ADMIN SET USERSCOUNT = ? WHERE ADMINUSERNAME = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,count-1)
            ibm_db.bind_param(stmt,2,'admin12')
            ibm_db.execute(stmt)
            
            customers = []
            sql = "SELECT * FROM USERS"
            stmt = ibm_db.exec_immediate(conn, sql)
            dictionary = ibm_db.fetch_both(stmt)
            while dictionary != False:
                customers.append(dictionary)
                dictionary = ibm_db.fetch_both(stmt)
            if customers:
                return render_template("deleteCustomersAdmin.html", customers = customers, msg="Delete successfully", username = session['ADMINUSERNAME'])
    return redirect(url_for('adminlog'))
    #return render_template("deleteCustomersAdmin.html", customers = customers, msg="Delete successfully", username = session['ADMINUSERNAME'])

@app.route('/viewAgents')
def viewAgents():
    if 'loggedin' in session:
        agents = []
        sql = "SELECT AGENTUSERNAME, AGENTEMAILADDRESS, AGENTTICKETS, AGENTTICKETSRESOLVED, NOTIFICATION FROM AGENTS"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            agents.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
        if agents:
            return render_template("viewAgentsAdmin.html", agents = agents, username = session['ADMINUSERNAME'])
    return redirect(url_for('adminlog'))

@app.route('/deleteAgents')
def deleteAgents():
    if 'loggedin' in session:
        agents = []
        sql = "SELECT AGENTUSERNAME, AGENTEMAILADDRESS, AGENTTICKETS, AGENTTICKETSRESOLVED, NOTIFICATION FROM AGENTS"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            agents.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
        if agents:
            return render_template("deleteAgentsAdmin.html", agents = agents, username = session['ADMINUSERNAME'])
    return redirect(url_for('adminlog'))

@app.route('/deleteAgents/<name>')
def deleteAgentsName(name):
    if 'loggedin' in session:
        sql = "SELECT * FROM AGENTS WHERE AGENTUSERNAME=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,name)
        ibm_db.execute(stmt)
        agent = ibm_db.fetch_row(stmt)
        if agent:
            sql = "DELETE FROM AGENTS WHERE AGENTUSERNAME=?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,name)
            ibm_db.execute(stmt)

            sql = "SELECT AGENTSCOUNT FROM ADMIN WHERE ADMINUSERNAME = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,'admin12')
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            count = int(account['AGENTSCOUNT'])
            
            sql = "UPDATE ADMIN SET AGENTSCOUNT = ? WHERE ADMINUSERNAME = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,count-1)
            ibm_db.bind_param(stmt,2,'admin12')
            ibm_db.execute(stmt)

            agents = []
            sql = "SELECT * FROM AGENTS"
            stmt = ibm_db.exec_immediate(conn, sql)
            dictionary = ibm_db.fetch_both(stmt)
            while dictionary != False:
                agents.append(dictionary)
                dictionary = ibm_db.fetch_both(stmt)
            if agents:
                return render_template("deleteAgentsAdmin.html", agents = agents, msg="Delete successfully",username = session['ADMINUSERNAME'])
    return redirect(url_for('adminlog'))
#EDIT THISS
"""@app.route('/viewTickets')
def viewTickets():
    if 'loggedin' in session:
        tickets = []
        sql = "SELECT TICKETID, AGENTEMAILADDRESS, AGENTTICKETS, AGENTTICKETSRESOLVED, NOTIFICATION FROM AGENTS"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            # print ("The Name is : ",  dictionary)
            agents.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
        if agents:
            return render_template("deleteAgentsAdmin.html", agents = agents, username = session['ADMINUSERNAME'])
    return redirect(url_for('adminlog'))"""
@app.route('/agentdashboard')
def agentdashboard():
    if 'loggedin' in session:
        sql = "SELECT TOTALTICKETS FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,'admin12')
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg5 = int(account['TOTALTICKETS'])

        sql = "SELECT TOTALNOTIFICATIONS FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,'admin12')
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg6 = int(account['TOTALNOTIFICATIONS'])

        sql = "SELECT USERSCOUNT FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,'admin12')
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg7 = int(account['USERSCOUNT'])

        sql = "SELECT TICKETSRESOLVED FROM ADMIN WHERE ADMINUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,'admin12')
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg8 = int(account['TICKETSRESOLVED'])

        sql = "SELECT AGENTTICKETS FROM AGENTS WHERE AGENTUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['AGENTUSERNAME'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg11 = int(account['AGENTTICKETS'])

        sql = "SELECT AGENTTICKETSRESOLVED FROM AGENTS WHERE AGENTUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['AGENTUSERNAME'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg22 = int(account['AGENTTICKETSRESOLVED'])

        msg33 = msg11 - msg22

        sql = "SELECT NOTIFICATION FROM AGENTS WHERE AGENTUSERNAME = ?   "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['AGENTUSERNAME'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        msg44 = int(account['NOTIFICATION'])
    
        return render_template('agentdashboard.html', username=session['AGENTUSERNAME'], msg5 = msg5, msg6 = msg6, msg7 = msg7, msg8 = msg8, msg11 = msg11, msg22 = msg22, msg33 = msg33, msg44 = msg44)
    return redirect(url_for('agentlog'))

@app.route('/userlogout')
def userlogout():
   session.pop('loggedin', None)
   session.pop('USERNAME', None)
   session.pop('EMAILADDRESS', None)
   flash("Successfully Logged Out!!")
   return redirect(url_for('userlog'))

@app.route('/agentlogout')
def agentlogout():
   session.pop('loggedin', None)
   session.pop('AGENTUSERNAME', None)
   session.pop('AGENTEMAILADDRESS', None)
   flash("Successfully Logged Out!!")
   return redirect(url_for('agentlog'))


@app.route('/adminlogout')
def adminlogout():
   session.pop('loggedin', None)
   session.pop('ADMINUSERNAME', None)
   session.pop('ADMINEMAILADDRESS', None)
   flash("Successfully Logged Out!!")
   return redirect(url_for('adminlog'))



if __name__ == '__main__':
    app.run(debug = True, host ="0.0.0.0", port = 8080)
