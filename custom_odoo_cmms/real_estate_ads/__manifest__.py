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
    "installable":True,
    "application":True,
    "license": "LGPL-3"
}