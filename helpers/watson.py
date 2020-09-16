from ibm_watson import NaturalLanguageUnderstandingV1, ToneAnalyzerV3, VisualRecognitionV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, KeywordsOptions, SentimentOptions
from ibm_cloud_sdk_core.api_exception import ApiException

import traceback


class Watson:

    def __init__(self):

        self.nlu_authenticator = IAMAuthenticator('2FUOyBJ6aCeTlpwPUicemr61j8D4AJjjkpXHhJ93QD3X')
        self.natural_language_understanding = NaturalLanguageUnderstandingV1(
            version = '2019-07-12',
            authenticator = self.nlu_authenticator
        )

        self.tone_authenticator = IAMAuthenticator('jphH895SCgd2p0npkO1nlZyMiJ6RMsdRtveOxwd-rgCJ')
        self.tone_analyzer = ToneAnalyzerV3(
            version = '2019-07-12',
            authenticator = self.tone_authenticator
        )

        self.tone_analyzer.set_service_url('https://api.us-south.tone-analyzer.watson.cloud.ibm.com/instances/84e3997e-8019-4bb8-b387-176e0861c0c5')

        self.natural_language_understanding.set_service_url('https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/452262a6-1d21-4dac-a637-bbb96192a69f')

    def extractKeywords(self, text):

        try:
            response = self.natural_language_understanding.analyze(
                text=text,
                features=Features(
                    keywords = KeywordsOptions(
                        sentiment = True,
                        emotion = True
                    )
                ),
                language='en'
            ).get_result()

            # print(response)
        except Exception as e:
            return {'message':traceback.format_exc(), 'status':400, 'success':False}

        return {'data':response, 'success':True}

    def extractSentiment(self, text, keywords):
        try:
            if isinstance(keywords, str):
                if ',' in keywords:
                    keywords = keywords.split(',')
                else:
                    keywords = [keywords]
            else:
                # print(type(keywords))
                # print(keywords.keys())
                keywords = [word['text'] for word in keywords['keywords'] if(word['relevance']>0.50)]

            response = self.natural_language_understanding.analyze(
                text = text,
                features = Features(
                    sentiment = SentimentOptions(
                        targets = keywords,
                        document=True
                    )
                ),
                language='en'
            ).get_result()
            # print(response)
        except Exception as e:
            return {'message':traceback.format_exc(), 'status':400, 'success':False}

        return {'data':response, 'success':True}

    def extractTones(self, text):

        try:
            response = self.tone_analyzer.tone(
                {'text': text},
                content_type='application/json',
                language='en'
            ).get_result()

        except Exception as e:
            return {'message':traceback.format_exc(), 'status':400, 'success':False}

        return {'data':response, 'success':True}

