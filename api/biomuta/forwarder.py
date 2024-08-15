
'''
########

Script redirects users based on gene names (e.g., from a search box to a specific gene detail page)
'''

from flask import Flask, request, redirect
from pymongo import MongoClient
import html

def forward_genename_route(app, db):
    protein_collection = db['C_biomuta_protein']

    @app.route('/forwarder', methods=['GET', 'POST'])
    def forwarder():
        gene_name = request.args.get('gene', '').strip()
        
        # Sanitize input
        gene_name = html.escape(gene_name).replace("'", "").replace('"', "")
        
        if len(gene_name) > 15 or "'" in gene_name:
            return "Bad value for gene name!", 400

        # Query the MongoDB database with case insensitivity
        protein = protein_collection.find_one({"geneName": {"$regex": f"^{gene_name}$", "$options": "i"}})
        
        # Redirect based on the result
        if protein is not None:
            ac = protein['canonicalAc'][:-2]  
            url = f"/biomuta/branchview/{ac}"
        else:
            url = "/biomuta/norecord"

        return redirect(url)

