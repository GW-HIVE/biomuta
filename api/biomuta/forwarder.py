
'''
########

Script redirects users based on gene names (e.g., from a search box to a specific gene detail page)
'''

from flask import request, redirect
from flask_restx import Resource
from pymongo import MongoClient
import html

def forward_genename_route(api, db):
    class ForwardGeneName(Resource):
        def get(self):
            return self.forward_gene_name()

        def post(self):
            return self.forward_gene_name()

        def forward_gene_name(self):
            gene_name = request.args.get('gene', '').strip()
            
            # Sanitize input
            gene_name = html.escape(gene_name).replace("'", "").replace('"', "")
            
            if len(gene_name) > 15 or "'" in gene_name:
                return "Bad value for gene name!", 400

            # Query the MongoDB database with case insensitivity
            protein = db['C_biomuta_protein'].find_one({"geneName": {"$regex": f"^{gene_name}$", "$options": "i"}})
            
            # Redirect based on the result
            if protein is not None:
                ac = protein['canonicalAc'][:-2]  
                url = f"/biomuta/branchview/{ac}"
            else:
                url = "/biomuta/norecord"

            return redirect(url)

    # Register the resource with the API and the route
    api.add_resource(ForwardGeneName, '/forwarder')
