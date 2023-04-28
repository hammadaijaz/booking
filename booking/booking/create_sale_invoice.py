import frappe
from frappe import _
from frappe.utils import getdate, cstr
from collections import OrderedDict
from operator import itemgetter
from console import console




@frappe.whitelist()
def creating(name):

	# query = frappe.db.sql(""" 
	# 	SELECT 
		
	#     COUNT(`tabTask`.`name`) as "No. of Tasks"


	# 	FROM  `tabProject`
	# 	LEFT JOIN `tabTask` ON `tabProject`.`name` = `tabTask`.`project`
	  

		
	# 	WHERE  `tabProject`.`name`='{}' """.format(name), as_list=True)


	query = frappe.db.count('Task', {'project': name})
	print(query)
	print()
	db = frappe.db.set_value('Project', name , 'task_count', query-1)

	console("task db value").log()
	console(query-1).log()
	console("Project db value").log()
	console(db).log()

	try:
		return query-1,db
	except:
		frappe.throw("Please select the correct Project")




from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def create_sale_invoice_from_lead(lead_name):
	console("enter hgya bhai ").log()
    # Fetch the Sales Order document
    lead = frappe.get_doc("Lead", lead_name)

    # Use a query to fetch the items from the Sales Order
    items = frappe.db.sql("""
        SELECT item_name,description,qty,rate
        FROM `tabBOM Details`
        WHERE parent=%s
    """, lead_name, as_dict=True)

    # Create a new Delivery Note document and set its fields
    sales_invoice = frappe.new_doc("Sales Invoice")
    sale_invoice.customer = lead.customer
    sale_invoice.posting_date = lead.posting_date
    sale_invoice.posting_time = lead.set_posting_time
    sale_invoice.due_date = lead.posting_date
    sale_invoice.currency = 'PKR'
    sale_invoice.selling_price_list = 'Standard Selling'
    sale_invoice.debit_to = '1310 - Debtors - BM'
    sale_invoice.company = 'Booking Management'

    # Loop through the items and add them to the Delivery Note
    for item in items:
    	console("agya loop me").log()
        sales_invoice.append("items", {
        item_code:item.item_name,
        description:'Biryani',
        qty:'1',
        uom:'Kg',
        conversion_factor:'1',
        rate:'12',
        amount:'123',
        income_account:'4110 - Sales - BM',
        cost_center:'Main - BM' 
                        })

    # Save the Delivery Note
    sales_invoice.insert()

    # Return the name of the new Delivery Note document
    return sales_invoice.name

# In this example, we first fetch the Sales Order document using its name. Then we use a SQL query to fetch the items from the Sales Order document. We then create a new Delivery Note document and set its fields using data from the Sales Order. Finally, we loop through the items and add them to the Delivery Note document. Once the Delivery Note is fully populated, we save it and return its name.

# You can call this function with the name of a Sales Order document to create a new Delivery Note document based on its data.

