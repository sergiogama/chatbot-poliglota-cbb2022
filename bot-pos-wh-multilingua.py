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
    
    try:
        text = params["payload"]["output"]["generic"][0]["text"]
    except:
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_code"] = 202
        params["payload"]["context"]["skills"]["main skill"]["user_defined"]["translation_result_msg"] = 'Texto não recebido'
        return params

    try:
        language = params["payload"]["context"]["skills"]["main skill"]["user_defined"]["language"]
    except:
        language = 'pt'

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

    # set up translator
#TO DO
    authenticator = IAMAuthenticator('<API Key')
    language_translator = LanguageTranslatorV3(
        version='2022-08-22',
        authenticator=authenticator
    )
#TO DO
    language_translator.set_service_url('Service URL')    
    
    model_id = "pt-en"

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
    params["payload"]["output"]["generic"][0]["text"] = new_text
    return params

