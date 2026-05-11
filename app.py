from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
import string
app = Flask(__name__)
app.secret_key = 'secret-key-hehe'

def create_cost_matrix():
     cost_matrix = [[100, 75, 50, 100] for row in range(12)]
     return cost_matrix

# random ticket generator 
def generate_reservation_code(first_name, last_name, seat_row, seat_column):
    first_last = first_name[0].upper() + last_name[0].upper()
    randomize = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)) 
    return f"{first_last}{seat_row}{seat_column}-{randomize}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    '''
    create matrix
    make sure labels align with readme
    '''
    cost_matrix = create_cost_matrix()
    col_labels = ['A', 'B', 'C', 'D']
    errors = [] #create a variable to hold errors

    #step 1 - grab data from form
    if request.method == 'POST':
         first_name = request.form.get('first_name', '').strip()
         last_name = request.form.get('last_name', '').strip()
         seat_row = request.form.get('seat_row', '').strip()
         seat_col = request.form.get('seat_col', '').strip().upper()

    # error check
         if not first_name:
           errors.append('First name is required.')
         if not last_name:
          errors.append('Last name is required.')

         if not seat_row:
          errors.append('Insert a seat row.')
         else:
           try:
               seat_row = int(seat_row)
               if not (1 <= seat_row <= 12):
                 errors.append('Choose a valid row option between 1-12.')
           except ValueError:
             errors.append('Row must be a number.')

         if not seat_col:
          errors.append('Insert a seat column.')
         elif seat_col not in ['A', 'B', 'C', 'D']:
          errors.append('Column must be between A-D.')
    
         if errors:
          return render_template('reserve.html',
                           errors=errors,
                           taken={},
                           cost_matrix=cost_matrix,
                           col_labels=col_labels,
                           form=request.form)
    
         ticket = generate_reservation_code(first_name, last_name, seat_row, seat_col)
         cost = cost_matrix[seat_row - 1][col_labels.index(seat_col)]

         return redirect(url_for('confirm',
                            passenger_name=f"{first_name} {last_name}",
                            seat_row=seat_row,
                            seat_col=seat_col,
                            ticket=ticket,
                            cost=cost
                            ))





    return render_template('reserve.html',
                           errors=[],
                           taken={},
                           cost_matrix=cost_matrix,
                           col_labels=col_labels,
                           form={}
                           )

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
      '''
        login page

        GET & POST Methods utilized
        url_for to redirect
        '''
      if request.method == 'POST':
            username = request.form.get('username', '')
            password = request.form.get('password', '')

            if username == 'admin' and password == 'password':
                session['admin'] = username
                flash(f'Welcome, {username}!')
                return redirect(url_for('admin_dashboard'))
                
            else: 
                return render_template('admin_login.html', error='Invalid credentials, please try again.')
    
      return render_template('admin_login.html', error=None)

@app.route('/admin')
def admin_dashboard():
        if not session.get('admin'):
             return redirect(url_for('admin_login'))
        
        cost_matrix = create_cost_matrix()
        col_labels = ['A', 'B', 'C', 'D']
        

        return render_template('admin.html',
                               reservations=[],
                               taken={},
                               cost_matrix=cost_matrix,
                               col_labels=col_labels,
                               total_sales=0,
                               admin_user=session.get('admin'))

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/delete/<int:res_id>', methods=['POST'])
def delete_reservation(res_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    
    return redirect(url_for('admin_dashboard'))
    
@app.route('/confirm')
def confirm():
     return render_template('confirm.html',
                            passenger_name=request.args.get('passenger_name'),
                            seat_row=request.args.get('seat_row'),
                            seat_col=request.args.get('seat_col'),
                            ticket=request.args.get('ticket'),
                            cost=request.args.get('cost'))

if __name__ == '__main__':
    app.run(debug=True)