#!/usr/bin/env python
 
import json
import cookielib, urllib, urllib2
 
class HiveWebAPI:
    def __init__(self, dna_cgi, login, pswd):
        self._dna_cgi = dna_cgi
        self._login = login
        self._pswd = pswd
        self._cookie_jar = cookielib.CookieJar()
        self._opener_with_cookies = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._cookie_jar))
 
    def __enter__(self):
        # avoid accidental auth leak
        login_dict = {'login': self._login, 'pswd': self._pswd}
        del self._login
        del self._pswd
        self._cmdr('login', login_dict)
        return self
 
    def __exit__(self, exc_type, exc_value, traceback):
        self._cmdr('logout')
        urllib2.urlopen(self._dna_cgi, urllib.urlencode([('cmdr', 'logout')]))
 
    def _cmdr(self, cmdr, param_dict=None, empty_output_is_error=False):
        if not param_dict:
            param_dict = dict()
 
        param_dict['cmdr'] = cmdr
        f = self._opener_with_cookies.open(self._dna_cgi, urllib.urlencode(param_dict))
        txt = f.read()
 
        if not txt and empty_output_is_error:
            txt = "error: no results"
 
        if f.getcode() != 200 or txt[0:6] == "error:":
            raise urllib2.HTTPError(f.geturl(), f.getcode(), txt, f.info(), f)
 
        return txt
 
 
    def propget(self, ids):
        if isinstance(ids, (list, tuple)):
            ids = ",".join(ids)
        return self._cmdr('propget', {'mode': 'json', 'ids': ids}, True)
 
    def propset(self, json_txt):
        return self._cmdr('propset2', {'mode': 'json', 'parse': json_txt})


 
if __name__ == '__main__':
    
	with HiveWebAPI('https://hive.biochemistry.gwu.edu/dna.cgi', 'rykahsay@gmail.com', 'Nakfa123123;') as hive:
        
		propget_json_txt = hive.propget(258)
        	print("propget result = %s" % propget_json_txt)
 
        	obj1 = json.loads(propget_json_txt)
        	#obj1["name"] = "Hello"
 
        	#obj2 = json.loads(hive.propget(258)
        	#obj2["name"] = "World!"
 
        	#propset_result = json.loads(hive.propset(json.dumps([obj1, obj2])))
 
        	#for obj in propset_result:
            	#	print("object %s of type %s has been updated using propset", obj['_id'], obj['_type'])


