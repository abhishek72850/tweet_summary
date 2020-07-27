from ibm_watson import NaturalLanguageUnderstandingV1, ToneAnalyzerV3, VisualRecognitionV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, KeywordsOptions, SentimentOptions
from ibm_watson import ApiException


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

        self.natural_language_understanding.set_service_url('https://gateway-lon.watsonplatform.net/natural-language-understanding/api')

    def extractKeywords(self, text):

        try:
            response = self.natural_language_understanding.analyze(
                text=text,
                features=Features(
                    keywords = KeywordsOptions(
                        sentiment = True,
                        emotion = True
                    )
                )
            ).get_result()

            print(response)

        except ApiException as ex:
            return {'message':ex.message, 'status':ex.code, 'success':False}

        return {'data':response, 'success':True}

    def extractSentiment(self, text, keywords):
        try:
            if isinstance(keywords, str):
                if ',' in keywords:
                    keywords = keywords.split(',')
                else:
                    keywords = [keywords]
            else:
                keywords = [word['text'] for word in keywords['keywords'] if(word['relevance']>0.50)]

            response = self.natural_language_understanding.analyze(
                text = text,
                features = Features(
                    sentiment = SentimentOptions(
                        targets = keywords,
                        document=True
                    )
                )
            ).get_result()
            print(response)
        except ApiException as ex:
            return {'message':ex.message, 'status':ex.code, 'success':False}

        return {'data':response, 'success':True}

    def extractTones(self, text):

        try:
            response = self.tone_analyzer.tone(
                {'text': text},
                content_type='application/json'
            ).get_result()

        except ApiException as ex:
            return {'message':ex.message, 'status':ex.code, 'success':False}

        return {'data':response, 'success':True}

