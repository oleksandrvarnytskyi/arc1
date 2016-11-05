# coding: utf-8
from Cookie import SimpleCookie

RESPONSE_OK = '200 OK'
RESPONSE_ERROR = '404 Not Found'
HEADER = ('Content-Type', 'text/html; charset=utf-8')
COOKIE_FORM = """
\t\t\t<div style="position: relative">
\t\t\t\t<p style="position: fixed; bottom: 0"> page_visits = {} </p>
\t\t\t</div>"""


def set_cookies(environ):
    cookie = SimpleCookie()
    cookie['page_visits'] = retrieve_visits(environ)
    cookie_headers = ('Set-Cookie', cookie['page_visits'].OutputString())
    headers = [cookie_headers, HEADER]
    return headers


def retrieve_visits(environ):
    if 'HTTP_COOKIE' in environ:
        cookie = SimpleCookie(environ['HTTP_COOKIE'])
        visits = str(int(cookie['page_visits'].value)+1)
        return visits
    else:
        visits = '1'
        return visits


def handle_get(environ, start_response):
    query = environ['QUERY_STRING'].split('&')

    with open('get_form.html', 'r') as f:
        reply_html = f.read()

    row_html = """
    \t\t<tr>
    \t\t\t<td>{key}</td>
    \t\t\t<td>{val}</td>
    \t\t</tr>"""

    rows_param = {}
    for params in query:
        params = params.split('=')
        params[1] = params[1].replace('+', ' ')
        rows_param[params[0]] = params[1]

    rows_html = ''
    fieldnames = ('first_name', 'last_name', 'profession')
    for fieldname in fieldnames:
        if fieldname in rows_param.keys():
            rows_html += (row_html.format(key=fieldname,
                                          val=rows_param[fieldname]))
        else:
            return handle_error(environ, start_response)
    start_response(RESPONSE_OK, set_cookies(environ))
    rows_html += COOKIE_FORM.format(retrieve_visits(environ))
    reply_html = reply_html.replace('$ROWS$', rows_html)
    return reply_html


def post_form():
    with open('form.html', 'r') as f:
        form = f.read()
    return form


def handle_post(environ, start_response):
    if environ['REQUEST_METHOD'] == 'GET':
        start_response(RESPONSE_OK, [HEADER])
        return post_form()

    if environ['REQUEST_METHOD'] == 'POST':
        import cgi

        form = cgi.FieldStorage(fp=environ['wsgi.input'],
                                environ=environ)
        fieldnames = ('name', 'sex', 'education', 'comment', 'spam')
        with open('get_form.html', 'r') as f:
            reply_html = f.read()
        row_html = """
        \t<tr>
        \t\t<td>{key}</td>
        \t\t<td>{val}</td>
        \t</tr>"""
        rows_html = ''
        for fieldname in fieldnames:
            rows_html += (row_html.format(key=fieldname.capitalize(),
                                          val=form.getvalue(fieldname)))
        start_response(RESPONSE_OK, set_cookies(environ))
        rows_html += COOKIE_FORM.format(retrieve_visits(environ))

        reply_html = reply_html.replace('$ROWS$', rows_html)
        return reply_html


def handle_error(environ, start_response):
    start_response(RESPONSE_ERROR, [HEADER])
    return ["<h1 style='color:red'>Invalid request</h1>"]


def application(environ, start_response):
    with open('log_env.txt', 'w') as f:
        f.write(str(environ))

    path = environ['PATH_INFO'].strip('/').split('/')
    if path[0] == '':
        start_response(RESPONSE_OK, set_cookies(environ))
        text_html = "<h1 style='color:blue'>Hello Web!</h1>"
        cookie = COOKIE_FORM.format(retrieve_visits(environ))
        return ["<html>", text_html, cookie, "</html>"]

    handler_name = 'handle_' + path[0]
    handler = globals().get(handler_name, handle_error)

    return handler(environ, start_response)
