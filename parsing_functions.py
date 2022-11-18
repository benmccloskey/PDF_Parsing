class pdfParser:
    def __init__(self):
        return
    
    @staticmethod 
    def get_emails(text: str) -> set:
        """A function that accepts a string of text and
            returns any email addresses located within the 
            text
            
            Parameters:
            text (str): A string of text
            
            Returns:
            set(emails): A set of emails located within
            the string of text.
        """
        email_pattern = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
        email_set = set()
        email_set.update(email_pattern.findall(text))
  
        return email_set

    @staticmethod
    def get_dates(text: str, info_dict_pdf : dict) -> set:
        date_label = ['DATE']
        nlp = spacy.load('en_core_web_lg')
        doc = nlp(text)
     

        dates_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
        dates = set((ent.text) for ent in doc.ents if ent.label_ in date_label)
        filtered_dates = set(date for date in dates if not dates_pattern.match(date))
                             
        return filtered_dates
    
    @staticmethod
    def get_citations(text: str):
        cit_pattern = re.compile(r'\[\d{0,3}\].*\d{4}', re.IGNORECASE)
        cit_set = set()
        cit_set.update(cit_pattern.findall(text))
        
        citations = list(cit_set)
        for i in range(len(citations)):
            citations = [x for x in citations[i].split('[')]
            
        cit_list = list()
        for i in range(len(citations)):
            if citations[i][len(citations[i])-6:-1].strip('.').lstrip().isdigit() == True:
                cit_list.append(citations[i].split(']')[1].lstrip())
            else:
                continue
        
        return cit_list
