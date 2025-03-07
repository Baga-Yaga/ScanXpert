from flask import Flask, request, render_template

app = Flask(__name__,template_folder='templates')

@app.route('/')
def greet():
	return render_template('home.html')

@app.route('/welcome/<name>')
def greet1(name):
    return f"Welcome, {name}"

@app.route('/add/<int:n1>/<int:n2>')
def add(n1,n2):
    return f"{n1} + {n2} = {n1 + n2}"
 
@app.route('/hello',methods=['POST','GET'])
def hello():
    if request.method == 'GET':
        return 'This is GET request'
    elif request.method == 'POST':
        return 'This is POST request'
    else:
        return 'No, man not allowed'

@app.route('/selfintro')
def signup():
    # name = request.args['Name']
    # std = request.args['class']
    # roll = request.args['roll']
    info = {"Name":"Atharva Sultanpure", "Class":"TY CSE-C", "Roll":"66"}
    return render_template('selfinto.html',info=info)

@app.route('/test',methods=['GET'])
def test():      
        # isadmin=False
        if 'name' in request.args.keys() or 'isadmin' in request.args.keys():
               isadmin = request.args['isadmin']
               name = request.args.get('name')
               if isadmin == "yes":
                   return "Welcome, Admin",200  
               else:
                   return f'Welcome, {name}',200
        else:
               return f'Give some name broo...',404

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/subdomain_enum')
def subdomain_enum():
    return render_template('subdomain_enum.html')

@app.route('/network_scan')
def network_scan():
    return render_template('network_scan.html')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5555, debug=True)

