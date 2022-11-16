import pandas as pd 
import dash 
import plotly.express as px 
from dash import dcc, Dash, html, dash_table
import base64
import datetime
import io
import plotly.graph_objs as go
import PyPDF2
from dash.dependencies import Input, Output, State
import base64
import os
from urllib.parse import quote as urlquote
from flask import Flask, send_from_directory
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import re
import json
import dash_bootstrap_components as dbc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG],suppress_callback_exceptions=True)

def make_break(num_breaks):
    br_list = [html.Br()] * num_breaks
    return br_list


class pdfReader:    
    def __init__(self, file_path: str) -> str:
        self.file_path = file_path
    
    def PDF_one_pager(self) -> str:
        """A function that accepts a file path to a pdf
            as input and returns a one line string of the 
            pdf.
            
            Parameters:
            file_path(str): The file path to the pdf.
            
            Returns:
            one_page_pdf (str): A one line string of the pdf.
        
        """
        content = ""
        p = open(self.file_path, "rb")
        pdf = PyPDF2.PdfFileReader(p)
        num_pages = pdf.numPages
        for i in range(0, num_pages):
            content += pdf.getPage(i).extractText() + "\n"
        content = " ".join(content.replace(u"\xa0", " ").strip().split())
        page_number_removal = r"\d{1,3} of \d{1,3}"
        page_number_removal_pattern = re.compile(page_number_removal, re.IGNORECASE)
        content = re.sub(page_number_removal_pattern, '',content)
        
        return content
  
    def pdf_reader(self) -> str:
        """A function that can read .pdf formatted files 
            and returns a python readable pdf.
            
            Parameters:
            self (obj): An object of the class IntelPdfReader
            
            Returns:
            read_pdf: A python readable .pdf file.
        """
        opener = open(self.file_path,'rb')
        read_pdf = PyPDF2.PdfFileReader(opener)
    
        return read_pdf
  
  
    def pdf_info(self) -> dict:
        """A function which returns an information dictionary
        of an object associated with the IntelPdfReader class.
        
        Parameters:
        self (obj): An object of the IntelPdfReader class.
        
        Returns:
        dict(pdf_info_dict): A dictionary containing the meta
        data of the object.
        """
        opener = open(self.file_path,'rb')
        read_pdf = PyPDF2.PdfFileReader(opener)
        pdf_info_dict = {}
        for key,value in read_pdf.documentInfo.items():
            pdf_info_dict[re.sub('/',"",key)] = value
        return pdf_info_dict
  
    def pdf_dictionary(self) -> dict:
        """A function which returns a dictionary of 
            the object where the keys are the pages
            and the text within the pages are the 
            values.
            
            Parameters:
            obj (self): An object of the IntelPdfReader class.
            
            Returns:
            dict(pdf_dict): A dictionary of the object within the
            IntelPdfReader class.
        """
        opener = open(self.file_path,'rb')
        #try:
        #    file_path = os.path.exists(self.file_path)
        #    file_path = True
        #break
        #except ValueError:
        #   print('Unidentifiable file path')
        read_pdf = PyPDF2.PdfFileReader(opener)
        length = read_pdf.numPages
        pdf_dict = {}
        for i in range(length):
            page = read_pdf.getPage(i)
            text = page.extract_text()
            pdf_dict[i] = text
            return pdf_dict

    def get_publish_date(self) -> str:
        """A function of which accepts an information dictionray of an object
            in the IntelPdfReader class and returns the creation date of the
            object (if applicable).
            
            Parameters:
            self (obj): An object of the IntelPdfReader class
            
            Returns:
            pub_date (str): The publication date which is assumed to be the 
            creation date (if applicable).
        """
        info_dict_pdf = self.pdf_info()
        pub_date= 'None'
        try:
            publication_date = info_dict_pdf['CreationDate']
            publication_date = datetime.strptime(publication_date.replace("'", ""), "D:%Y%m%d%H%M%S%z")
            pub_date = publication_date.isoformat()[0:10] 
        except:
            pass
        return pub_date
    
directory = '/Users/benmccloskey/Desktop/pdf_dashboard/files'

# for filename in os.listdir(directory):
#     f = os.path.join(directory, filename)
#     if os.path.isfile(f): 
#         try:
#             pdf = pdfReader(f)
#             text = pdf.PDF_one_pager()
#             df = pd.DataFrame([text])
#         except:
#             pass
# df = pd.DataFrame([text])
    


app.layout = html.Div(children =[html.Div(children =[html.H1(children='PDF Parser', 
                                          style = {'textAlign': 'center',
                                                   'color' : '#7FDBFF',})]),
                                 
                                 
html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ), 
    #Returns info, above the datatable,
    html.Div(id='output-datatable'),
    html.Div(id='output-data-upload')#output for the datatable,
]),
                                                       

  ])
                                                       
                                                       
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'pdf' in filename:
            pdf = pdfReader(directory + '/' + filename)
            text = pdf.PDF_one_pager()
            df = pd.DataFrame({'Text':[text]})
            #return html.Div(text)
    except Exception as e:
        print(e)
        return df,html.Div([
            'There was an error processing this file.'
        ])
    

    return html.Div([
        html.H5(filename),#return the filename
        html.H6(datetime.datetime.fromtimestamp(date)),#edit date
        dcc.Checklist(id='checklist',options = [
            {"label": "Text", "value": "Text"},
            {"label": "Date", "value": "Date"},
            {"label": "Email Addresses", "value": "Email Addresses"}
        ],
            value = ['Text']),

      #   dash_table.DataTable(
      #       df.to_dict('records'),
      #       [{'name': i, 'id': i} for i in df.columns],
      #       style_data={
      #           'whiteSpace': 'normal',
      #           'height': 'auto',
      #           'textAlign': 'left',
      #             'backgroundColor': 'rgb(50, 50, 50)',
      #             'color': 'white'},
      #       style_header={'textAlign' : 'left',
      #               'backgroundColor': 'rgb(30, 30, 30)',
      #               'color': 'white'
      #               },
      # ),
        html.Hr(),
        dcc.Store(id='stored-data' ,data = df.to_dict('records')),

        html.Hr(),  # horizontal line

    ])

@app.callback(Output('output-datatable', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(Output('output-data-upload', 'children'),
              Input('checklist','value'),
              Input('stored-data', 'data'))

def table_update(options_chosen, df_dict):
    if options_chosen == []:
        return options_chosen == []
    df_copy = pd.DataFrame(df_dict)
    value_dct = {}
    for val in options_chosen:
        if val == 'Text':
            text = df_copy.Text
            value_dct[val] = text
        if val == 'Date':
            value_dct[val] = ['this is a test']
    dff =  pd.DataFrame(value_dct)
    return dash_table.DataTable(
            dff.to_dict('records'),
            [{'name': i, 'id': i} for i in dff.columns],
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'textAlign': 'left',
                  'backgroundColor': 'rgb(50, 50, 50)',
                  'color': 'white'},
            style_header={'textAlign' : 'left',
                    'backgroundColor': 'rgb(30, 30, 30)',
                    'color': 'white'
                    })

if __name__ == '__main__':
    app.run_server(debug=True)
