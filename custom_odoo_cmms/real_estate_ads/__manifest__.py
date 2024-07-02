{
    "name": "Real Estate Ads",
    "version": "1.0",
    "website": "https//www.technetiumweb.com",
    "author": "Aro Mondezie",
    "description": """
        Real Estate module to show available properties
    """,
    "category": "Sales",
    "depends": ['base'],
    "data": [
        'security/ir.model.access.csv',
        'views/property_view.xml',
        'views/property_type_view.xml',
        'views/property_tag_view.xml',
        'views/menu_items.xml',

        # Data Files:
        # Step 23A : Working with Data Files
        'data/property_type.xml'
        #'data/estate.property.type.csv'   ### A TEST EXAMPLE CSV FILE TO RECORD DATA: the same as 'data/property_type.xml'
    ],
    #  Step 23b : Working with Data Files: CREATE RECORDS with Demo Data
    'demo': [
        'demo/property_tag.xml',# These DEMO DATA will NEVER be CREATED if I did not ENABLE DEMO DATA AT the creation of my database
    ],
    "installable":True,
    "application":True,
    "license": "LGPL-3"
}