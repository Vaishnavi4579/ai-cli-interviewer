from web_app import app
with app.test_client() as c:
    rv = c.post('/interview', data={'resume_text':'Experienced candidate with Python and testing.'})
    print('STATUS', rv.status_code)
    data = rv.data.decode('utf-8')
    print(data[:800])
