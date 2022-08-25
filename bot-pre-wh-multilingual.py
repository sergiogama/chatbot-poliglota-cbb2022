#
#
# main() will be run when you invoke this action
#
# @param Cloud Functions actions accept a single parameter, which must be a JSON object.
#
# @return The output of this action, which must be a JSON object.
#
#
#import sys, json

import json
from ibm_watson import LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# consts
LT_THRESH = 0.4

def main( params ):
    
    #If welcome message - No process to be done
    try: 
        skills = params["payload"]["context"]["skills"]
    except:
        return params
        
    try:
        text = params["payload"]["input"]["text"]
    except:
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_code"] = 202
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_msg"] = 'Texto não recebido'
        return params

    try:
        language = params["payload"]["context"]["skills"]["main skill"]["user_defined"]["language"]
    except:
        language = 'pt'

    # set up translator
#TO DO
    authenticator = IAMAuthenticator('<API Key')
    language_translator = LanguageTranslatorV3(
        version='2022-08-22',
        authenticator=authenticator
    )
#TO DO
    language_translator.set_service_url('<Service URL>')    
    
    # Identify language
    try:
        lt_lang = language_translator.identify(text).get_result()
    except:
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_code"] = 203
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_msg"] = 'Erro na chamada do servço para identificar idioma'
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["language"] = language
        return params

    if lt_lang and lt_lang['languages'][0]['confidence'] > LT_THRESH:
        language = lt_lang['languages'][0]['language']
    else:
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_code"] = 204
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_msg"] = 'Não foi possivel identificar idioma'
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["language"] = language
        return params

    if language is None:
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_code"] = 205
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_msg"] = 'Não foi possivel identificar idioma'
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["language"] = language
        return params

    if language == 'pt':
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_code"] = 200
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_msg"] = 'Texto em português, mantido o original'
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["language"] = language
        return params

    if language != 'en':
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_code"] = 206
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_msg"] = 'Idioma não suportado'
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["language"] = 'pt'
        return params

    params["payload"]["context"]["skills"]["main skill"]["user_defined"]["language"] = language

    model_id = "en-pt"

    # translate to base language if needed
    try:
        translation = language_translator.translate(
        text=text,
        model_id=model_id).get_result()
    except:
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_code"] = 208
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_msg"] = 'Erro no serviço de tradução'
        return params

    try:
        new_text = translation['translations'][0]['translation']
    except:
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_code"] = 209
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_msg"] = 'Texto traduzido não recuperado'
        return params

    #Success
    params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_code"] = 200
    params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_msg"] = 'Traduzido com sucesso'
    params["payload"]["context"]["skills"]["main skill"]["user_defined"]["original_input"] = text
    params["payload"]["input"]["text"] = new_text
    return params

