from flask import Flask,render_template, request,redirect,Response,jsonify
import mysql.connector
import os
import io
import csv
from datetime import datetime


app=Flask(__name__,template_folder="template")

app.secret_key = os.getenv("SECRET_KEY", "Cosmo or no other")


db = mysql.connector.connect(
    host="localhost",
    username="root",
    password ="Root!234",
    database="member_care"
)

# db = mysql.connector.connect(
#     host=os.getenv("DB_HOST", "localhost"),
#     username=os.getenv("DB_USER", "root"),
#     password=os.getenv("DB_PASSWORD", "Root!234"),
#     database=os.getenv("DB_NAME", "member_care"),
#     port=int(os.getenv("DB_PORT", 3306)),
# )

cursor = db.cursor(dictionary=True)


@app.route('/')
def select_form():
    return render_template('all_forms.html')  # This page should have links to each form

# Routes to render HTML forms for each category
@app.route('/form/pre_authorization')
def pre_authorization_form():
    return render_template('pre_authorization.html')

@app.route('/form/dental_optical')
def dental_optical_form():
    return render_template('Dental_optical_authorization.html')

@app.route('/form/client_call')
def client_call_form():
    return render_template('client_call.html')

@app.route('/form/providers_call')
def providers_call_form():
    return render_template('provider_call.html')

@app.route('/form/report', methods=['GET', 'POST'])
def report_page():
    return render_template('Report.html')



# Routes to handle form submissions for each category

from flask import flash, redirect, request

@app.route('/submit/pre_authorization', methods=['POST'])
def submit_pre_authorization():
    try:
        escalated_to = request.form.get('escalated_to',None)
        data = (
            request.form['service_provider'], request.form['company'],
            request.form['member_name'], request.form['member_number'],
            request.form['authorization_type'], request.form['authorization_details'],
            float(request.form['amount']), request.form['officer'],
            request.form['status'],
            escalated_to
        )
        cursor.execute(
            "INSERT INTO pre_authorization (service_provider, company, member_name, member_number, authorization_type, authorization_details, amount, officer, status,escalated_to) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            data
        )
        db.commit()
        flash("Pre-authorization submitted successfully!", "success")
    except Exception as e:
        db.rollback()
        flash(f"An error occurred: {e}", "danger")
    return redirect('/')

@app.route('/submit/dental_optical', methods=['POST'])
def submit_dental_optical():
    try:
        escalated_to = request.form.get('escalated_to',None)
        data = (
            request.form['service_provider'], request.form['company'],
            request.form['member_name'], request.form['member_number'],
            request.form['authorization_type'], request.form['authorization_details'],
            float(request.form['amount']), request.form['officer'],
            request.form['status'],
            escalated_to
        )
        cursor.execute(
            "INSERT INTO dental_optical_authorization (service_provider, company, member_name, member_number, authorization_type, authorization_details, amount, officer, status,escalated_to) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)",
            data
        )
        db.commit()
        flash("Dental/Optical authorization submitted successfully!", "success")
    except Exception as e:
        db.rollback()
        flash(f"An error occurred: {e}", "danger")
    return redirect('/')

@app.route('/submit/client_call', methods=['POST'])
def submit_client_call():
    try:
        escalated_to = request.form.get('escalated_to',None)
        data = (
            request.form['company'], request.form['member_name'],
            request.form['membership_number'], request.form['call_details'],
            int(request.form['call_duration']), request.form['officer'],
            request.form['status'],
            escalated_to
        )
        cursor.execute(
            "INSERT INTO client_call (company, member_name, membership_number, call_details, call_duration, officer, status,escalated_to) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            data
        )
        db.commit()
        flash("Client call submitted successfully!", "success")
    except Exception as e:
        db.rollback()
        flash(f"An error occurred: {e}", "danger")
    return redirect('/')

@app.route('/submit/providers_call', methods=['POST'])
def submit_providers_call():
    escalated_to = request.form.get('escalated_to',None)
    try:
        data = (
            request.form['service_provider'], request.form['call_details'],
            int(request.form['call_duration']), request.form['officer'],
            request.form['status'], request.form['attendant_name'],
            request.form['contact'], request.form['member_number'],
            escalated_to
        )
        cursor.execute(
            "INSERT INTO providers_call (service_provider, call_details, call_duration, officer, status, attendant_name, contact, member_number,escalated_to) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            data
        )
        
        db.commit()
        flash("Provider's call submitted successfully!", "success")
    except Exception as e:
        db.rollback()
        flash(f"An error occurred: {e}", "danger")
    return redirect('/')


#viewing the database
@app.route('/view/pre_authorization')
def view_pre_authorization():
    cursor.execute("SELECT * FROM pre_authorization")
    calls = cursor.fetchall()
    report = generate_report('pre_authorization')
    return render_template('view_pre_authorization.html', calls=calls, report=report)

@app.route('/view/dental_optical')
def view_dental_optical():
    cursor.execute("SELECT * FROM dental_optical_authorization")
    calls = cursor.fetchall()
    report = generate_report('dental_optical_authorization')
    return render_template('view_dental_optical.html', calls=calls, report=report)

@app.route('/view/client_call')
def view_client_call():
    cursor.execute("SELECT * FROM client_call")
    calls = cursor.fetchall()
    report = generate_report('client_call')
    return render_template('view_client_call.html', calls=calls, report=report)

@app.route('/view/providers_call')
def view_providers_call():
    cursor.execute("SELECT * FROM providers_call")
    calls = cursor.fetchall()
    report = generate_report('providers_call')
    
    return render_template('view_providers_call.html', calls=calls, report=report)



# def generate_report(table_name):
#     # Total calls
#     cursor.execute(f"SELECT COUNT(*) AS total_calls FROM {table_name}")
#     total_calls = cursor.fetchone()['total_calls']
    
#     # Resolved calls
#     cursor.execute(f"SELECT COUNT(*) AS resolved_calls FROM {table_name} WHERE status = 'Resolved'")
#     resolved_calls = cursor.fetchone()['resolved_calls']
    
#     # Calculate pending calls
#     pending_calls = total_calls - resolved_calls
    
#     # Return as a dictionary
#     return {
#         'total_calls': total_calls,
#         'resolved_calls': resolved_calls,
#         'pending_calls': pending_calls
#     }
def generate_report(table_name):
    # Total calls
    cursor.execute(f"SELECT COUNT(*) AS total_calls FROM {table_name}")
    total_calls = cursor.fetchone()['total_calls'] or 0
    print("Total calls:", total_calls)
    
    # Resolved calls (assuming 'Approved' means resolved)
    cursor.execute(f"SELECT COUNT(*) AS resolved_calls FROM {table_name} WHERE status = 'Approved'")
    resolved_calls = cursor.fetchone()['resolved_calls'] or 0
    print("Resolved calls (Approved):", resolved_calls)
    
    # Unresolved calls (assuming 'Unapproved' means unresolved)
    cursor.execute(f"SELECT COUNT(*) AS unresolved_calls FROM {table_name} WHERE status = 'Unapproved'")
    unresolved_calls = cursor.fetchone()['unresolved_calls'] or 0
    print("Unresolved calls (Unapproved):", unresolved_calls)
    
    # Pending calls (explicitly labeled as 'Pending')
    cursor.execute(f"SELECT COUNT(*) AS escalated_calls FROM {table_name} WHERE status = 'Escalated'")
    result = cursor.fetchone()['escalated_calls']
    escalated_calls = result['escalated_calls'] if result and 'escalated_calls' in result else 0
    print("Escalated call results:", result)
    
    # Return as a dictionary
    return {
        'total_calls': total_calls,
        'resolved_calls': resolved_calls,
        'unresolved_calls': unresolved_calls,
        'escalated_calls': escalated_calls
    }

#for downloads
def generate_csv(query, headers):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)  # Write the header row

    cursor.execute(query)
    for row in cursor.fetchall():
        writer.writerow(row.values())  # Write rows fetched from the database

    output.seek(0)  # Reset the stream position
    return output

# Route for downloading all concatenated data
@app.route('/download/all', methods=['GET'])
def download_all():
    queries = [
        ("SELECT * FROM pre_authorization", ["Service Provider", "Company", "Member Name", "Member Number", "Auth Type", "Auth Details", "Amount", "Officer", "Date Created", "Status"]),
        ("SELECT * FROM dental_optical_authorization", ["Service Provider", "Company", "Member Name", "Member Number", "Auth Type", "Auth Details", "Amount", "Officer", "Date Created", "Status"]),
        ("SELECT * FROM providers_call", ["Service Provider", "Call Details", "Call Duration", "Officer", "Date Created", "Status", "Attendant Name", "Contact", "Member Number"]),
        ("SELECT * FROM client_call", ["Company", "Member Name", "Membership Number", "Call Details", "Call Duration", "Officer", "Date Created", "Status"])
    ]

    combined_output = io.StringIO()
    writer = csv.writer(combined_output)

    for query, headers in queries:
        writer.writerow(headers)  # Write headers for each table
        cursor.execute(query)
        for row in cursor.fetchall():
            writer.writerow(row.values())  # Write rows for the table
        writer.writerow([])  # Add blank line between tables

    combined_output.seek(0)
    return Response(
        combined_output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=all_forms.csv"}
    )

# Route for downloading individual forms
@app.route('/download/<form_type>', methods=['GET'])
def download_form(form_type):
    # Map form types to queries and headers
    forms = {
        'pre_authorization': (
            "SELECT * FROM pre_authorization",
            ["Service Provider", "Company", "Member Name", "Member Number", "Auth Type", "Auth Details", "Amount", "Officer", "Date Created", "Status"]
        ),
        'dental_optical': (
            "SELECT * FROM dental_optical_authorization",
            ["Service Provider", "Company", "Member Name", "Member Number", "Auth Type", "Auth Details", "Amount", "Officer", "Date Created", "Status"]
        ),
        'providers_call': (
            "SELECT * FROM providers_call",
            ["Service Provider", "Call Details", "Call Duration", "Officer", "Date Created", "Status", "Attendant Name", "Contact", "Member Number"]
        ),
        'client_call': (
            "SELECT * FROM client_call",
            ["Company", "Member Name", "Membership Number", "Call Details", "Call Duration", "Officer", "Date Created", "Status"]
        )
    }

    if form_type not in forms:
        return "Invalid form type", 400

    query, headers = forms[form_type]
    csv_file = generate_csv(query, headers)
    return Response(
        csv_file.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={form_type}.csv"}
   )

@app.route('/download', methods=['GET'])
def download():
    # Get the selected form type and date range from query parameters
    form_type = request.args.get('form_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date or not end_date:
        return "Start date and end date are required", 400

    # Queries and headers for each form type
    forms = {
        'pre_authorization': (
            "SELECT * FROM pre_authorization WHERE date_created BETWEEN %s AND %s",
            ["Service Provider", "Company", "Member Name", "Member Number", "Auth Type", "Auth Details", "Amount", "Officer", "Date Created", "Status"]
        ),
        'dental_optical': (
            "SELECT * FROM dental_optical_authorization WHERE date_created BETWEEN %s AND %s",
            ["Service Provider", "Company", "Member Name", "Member Number", "Auth Type", "Auth Details", "Amount", "Officer", "Date Created", "Status"]
        ),
        'providers_call': (
            "SELECT * FROM providers_call WHERE date_created BETWEEN %s AND %s",
            ["Service Provider", "Call Details", "Call Duration", "Officer", "Date Created", "Status", "Attendant Name", "Contact", "Member Number"]
        ),
        'client_call': (
            "SELECT * FROM client_call WHERE date_created BETWEEN %s AND %s",
            ["Company", "Member Name", "Membership Number", "Call Details", "Call Duration", "Officer", "Date Created", "Status"]
        )
    }

    # Handle individual forms
    if form_type != 'all':
        if form_type not in forms:
            return "Invalid form type selected", 400

        query, headers = forms[form_type]
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()

        csv_file = generate_csv_from_rows(rows, headers)
        return Response(
            csv_file.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={form_type}_filtered.csv"}
        )

    # Handle combined "All Forms"
    combined_output = io.StringIO()
    writer = csv.writer(combined_output)

    for form, (query, headers) in forms.items():
        writer.writerow([form.upper()])  # Section Header
        writer.writerow(headers)  # Column Headers
        cursor.execute(query, (start_date, end_date))
        for row in cursor.fetchall():
            writer.writerow(row.values())
        writer.writerow([])  # Add a blank line between sections

    combined_output.seek(0)
    return Response(
        combined_output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=all_forms_filtered.csv"}
    )


def generate_csv_from_rows(rows, headers):
    """
    Helper function to generate CSV data from rows and headers.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)  # Write headers
    for row in rows:
        writer.writerow(row.values())  # Write rows
    output.seek(0)
    return output




if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000,debug=True)