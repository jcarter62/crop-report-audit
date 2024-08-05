import os
from flask import Flask, request, jsonify, send_file, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv
import logging
import pandas as pd
from io import BytesIO
from waitress import serve

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')

db = SQLAlchemy(app)

logging.basicConfig(level=logging.INFO)


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/save_years', methods=['POST'])
def save_years():
    current_year = request.form['current_year']
    compare_year = request.form['compare_year']
    response = {'current_year': current_year, 'compare_year': compare_year}
    return jsonify(response)


@app.route('/generate_report')
def generate_report():
    current_year = "'" + request.args.get('current_year', default='2024', type=str) + "'"
    compare_year = "'" + request.args.get('compare_year', default='2023', type=str) + "'"

    sqls = f"""
    SELECT 
    y.CropYear as LastYear, y.CropCode as LastYearCC, yc.CropName as LastYearCN,
    y.NonBearing as LastYear_NonBearing, y.NotHarvested as LastYear_NotHarvested,
    CASE 
    WHEN c.CropCode <> y.CropCode THEN 'X'
    ELSE ''
    END as Diff,
    c.CropYear, c.DateEntered, c.Field_ID, f.FieldName, c.CropAcres, c.CropCode, cc.CropName,
    c.NonBearing, c.NotHarvested,
    n.NAME_ID as Account, n.FullName as Account_Name
    FROM CropReport2010Data c 
    JOIN CropCodes cc ON c.CropCode = cc.CropCode
    LEFT JOIN CropReport2010Data y ON c.Field_ID = y.Field_ID AND y.CropYear = {compare_year}
    LEFT JOIN cropcodes yc ON y.CropCode = yc.CropCode
    JOIN fields f ON c.Field_ID = f.field_id
    JOIN name n ON f.NAME_ID = n.NAME_ID
    WHERE c.cropyear = {current_year} 
    ORDER BY n.NAME_ID, f.FieldName;
    """

    sql = text(sqls)

    result = db.session.execute(sql)
    columns = result.keys()
    data = result.fetchall()

    df = pd.DataFrame(data, columns=columns)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
    output.seek(0)

    return send_file(output,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True,
                     download_name='report.xlsx')


server_ip = os.getenv('SERVER_IP')
server_port = os.getenv('SERVER_PORT')
serve(app, host=server_ip, port=server_port)
