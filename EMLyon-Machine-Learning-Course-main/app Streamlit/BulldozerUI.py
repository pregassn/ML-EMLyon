
import os
import sys
from io import open


# for data and saves
import pandas as pd
import numpy as np
import dill
from PIL import Image # pillow package


# custom package
from emlyon_module.structured import *


# for app
import streamlit as st



#**********************************************************
#*                      functions                         *
#**********************************************************

# blogs on this topic
# https://blog.jcharistech.com/2019/11/28/summarizer-and-named-entity-checker-app-with-streamlit-and-spacy/
# https://blog.jcharistech.com/2019/12/14/building-a-document-redactor-nlp-app-with-streamlitspacy-and-python/

# ------------------------- Paths -------------------------
path_to_rep  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_to_data = os.path.join(path_to_rep, 'data', 'bulldozers')



# ------------------------- Utils -------------------------
from PatchStreamlit import (
    SessionState, 
    st_rerun,
)


# ------------------------- Layout ------------------------
def centerText(text, thick = 1) :
    '''Displays a text with centered indentation, with specified thickness (the lower, the thickier)'''
    st.markdown("<h{} style='text-align: center; color: black;'>{}</h{}>".format(thick, text, thick), unsafe_allow_html = True)
    return



# -------------------------- Tmp --------------------------
def display_bulldozer_img(index):
    centerText('Selected bulldozer', thick = 3)
    empty1, col, empty2 = st.beta_columns([2.5, 5, 2.5])
    ind = index % len(session_state.imgs) # congruence
    img = session_state.imgs[ind]
    with col:
        st.image(img, use_column_width = 'always')
    return


def display_bulldozer_price(index):
    # compute model prediction
    pred_price = session_state.model.predict([session_state.X.values[index]])[0]
    pred_price = int(np.exp(pred_price))
    true_price = int(np.exp(session_state.y[index]))

    # display actual and predicted prices
    col_price, col_pred = st.beta_columns(2)
    with col_price:
        centerText('real price', thick = 3)
        centerText(str(true_price) + ' Euros', thick = 4)
    with col_pred:
        centerText('estimated price', thick = 3)
        centerText(str(pred_price) + ' Euros', thick = 4)
    return


def display_bulldozer_features(index):
    centerText('Bulldozer features', thick = 3)
    feat0, val0, feat1, val1 = st.beta_columns([3.5, 1.5, 3.5, 1.5])
    row = session_state.X.values[index]
    for i, feature in enumerate(session_state.X.columns):
        ind = i % 2
        if ind == 0:
            with feat0:
                st.warning(feature)
            with val0:
                st.info(str(row[i]))
        elif ind == 1:
            with feat1:
                st.warning(feature)
            with val1:
                st.info(str(row[i]))
    return



#**********************************************************
#                     main script                         *
#**********************************************************


#st.sidebar.title('Bulldozer _viewer_')
#st.title('Bulldozer _viewer_')

# session state
session_state = SessionState.get(
    model = None,
    X = None,
    y = None,
    imgs = None,
)


# init session state
if session_state.model is None:
    # validation set given in notebook
    n_valid = 12000

    # load and preprocess data
    data = pd.read_csv(
        os.path.join(path_to_data, 'Train.csv'), 
        low_memory = False, 
        parse_dates = ["saledate"],
    )
    data.SalePrice = np.log(data.SalePrice)
    X, y, nas = proc_df(data, 'SalePrice')
    X, y = X[n_valid:], y[n_valid:]

    # load regression model
    path_to_model = os.path.join(path_to_rep, 'app Streamlit', 'saves', 'RF_regressor.pk')
    with open(path_to_model, 'rb') as file:
        model = dill.load(file)

    # load bulldozer images
    imgs = []
    path_to_imgs = os.path.join(path_to_rep, 'app Streamlit', 'img')
    img_files = os.listdir(path_to_imgs)
    for img_file in img_files:
        img = Image.open(os.path.join(path_to_imgs, img_file))
        img = np.array(img)
        imgs.append(img)

    # store in cache
    session_state.n_valid = n_valid
    session_state.X = X
    session_state.y = y
    session_state.model = model
    session_state.imgs = imgs




centerText('Choose a bulldozer', thick = 1)
st.write(' ')
st.write(' ')

index = st.selectbox(
    'select a bulldozer', 
    options = ['-'] + [i for i in range(1, session_state.n_valid + 1)],
    index = 0,
)

if type(index) == int:
    # bulldozer img
    display_bulldozer_img(index)

    # bulldozer price
    centerText('Bulldozer price', thick = 3)
    void0, col, void1 = st.beta_columns([4, 2, 4])
    with col:
        estimate = st.button('Estimate !')
    if estimate:
        display_bulldozer_price(index)

    # bulldozer features
    display_bulldozer_features(index)

