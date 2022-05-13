import streamlit as st
# Import os for the path
import os
# Library for the image
from PIL import Image
# Library for import the credential
import json
# Library for import azure form recognizer
from azure.ai.formrecognizer import FormRecognizerClient, FormTrainingClient
from azure.core.credentials import AzureKeyCredential   # For the credentials
from azure.core.exceptions import ResourceNotFoundError # For the exceptions

# Import the credential
credentials = json.load(open('./credential.json'))
API_KEY = credentials['API_KEY']
ENDPOINT = credentials['ENDPOINT']

# Configuration layout
st.set_page_config(layout="wide",initial_sidebar_state="expanded")


# TITLE
st.title("Convierte tus imagenes a texto ")

# SELECT TYPE IMAGE 
st.header("1️⃣ Seleccione el tipo de imagen")
choice = st.selectbox(
    'Tipo de imagen:',
    ('Recibos', 'Facturas', 'Documentos de identidad'))
st.write('Tu has seleccionado:', choice)
    
# UPLOAD IMAGE
st.header("2️⃣ Cargue la imagen")
image_file = st.file_uploader("", type=["png","jpg","jpeg"])
@st.cache
def load_image(image_file):
    img = Image.open(image_file)
    return img   

 
col1, col2 = st.columns(2)

with col1:
    
    st.header("3️⃣ Visualice la imagen")
    # DISPLAY IMAGE
    if image_file is not None:
        # To See details
        file_details = {"filename":image_file.name, "filetype":image_file.type, "filesize":image_file.size}
        #st.write(file_details)
        #st.write(image_file)    
        # To View Uploaded Image
        st.image(load_image(image_file),width=500)
        # Saving uploaded image
        with open(os.path.join("images",image_file.name),"wb") as f:
            f.write((image_file).getbuffer())
        #st.success("File Upload")
        # Path
        path_image = os.path.join("./images/",image_file.name)
        #st.write(path_image)
 
    

with col2:
    # RESULTS
    st.header("4️⃣ Resultados")
           
    # OPTION 1: RECIBOS 
    
    if choice == 'Recibos':
        # If Upload the image
        if image_file is not None:
            # Create a instance of FormRecognizerClient
            form_recognizer_client = FormRecognizerClient(ENDPOINT, AzureKeyCredential(API_KEY))
            # Pass image to client
            with open(path_image, "rb") as fd:
                    form = fd.read()
            # Recognize the content
            poller = form_recognizer_client.begin_recognize_receipts(form)      
            form_result = poller.result()   # Results 
            # Pages of the file
            for receipt in form_result:
                for name, field in receipt.fields.items():
                    if name == "Items":
                        #st.markdown("**Items**")
                        #st.markdown('---')
                        for idx, items in enumerate(field.value):
                            #st.markdown("**Item # {}**".format(idx+1))
                            for item_name, item in items.value.items():
                                st.markdown('**{} :** {} '.format(item_name,item.value))
                                #st.write("......{}: {} has confidence {}".format(item_name, item.value, item.confidence))
                    else:
                        st.markdown("**{} :** {} ".format(name, field.value)) 
    
    # OPTION 2: FACTURAS
    
    elif choice == 'Facturas':
        # If Upload the image
        if image_file is not None:
            # Create a instance of FormRecognizerClient
            form_recognizer_client = FormRecognizerClient(ENDPOINT, AzureKeyCredential(API_KEY))
            # Pass image to client
            with open(path_image, "rb") as fd:
                    form = fd.read()
            poller = form_recognizer_client.begin_recognize_invoices(form)
            result = poller.result()
            result[0].fields.keys()
            def extract_invoice_field_value(invoice, field_name):
                try:
                    if field_name == 'Items':
                        for item in invoice.fields.get('Items').value:
                            for key in item.value.keys():
                                st.markdown('**{} :** {}'.format(key, item.value.get(key).value))
                                #st.write('-'*25)
                                #st.write('\t' + str(item.value.get(key).value) + '|' + str(item.value.get(key).confidence))
                                st.write()
                    else:
                        #st.write(field_name)
                        #st.write('-'*25)
                        st.markdown('**{} :** {}'.format(field_name, invoice.fields.get(field_name).value))
                        #st.write(str(invoice.fields.get(field_name).value) + '|' + str(invoice.fields.get(field_name).confidence))
                except AttributeError:
                    st.write('Nothing is found')

            if poller.status() == 'succeeded':
                for page in result:
                    field_keys = page.fields.keys()
                    for field_key in field_keys:
                        extract_invoice_field_value(page, field_key)
    