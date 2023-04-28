# import frappe
# from frappe import _
# from console import console
# from frappe.model.mapper import get_mapped_doc
# import frappe
# from frappe.utils import cstr, getdate
# import json
# from frappe.utils.background_jobs import enqueue



# @frappe.whitelist()
# def no_of_task(name):

# 	query = frappe.db.sql(""" 
# 		SELECT 
		
# 	    COUNT(`tabTask`.`name`) as "No. of Tasks"


# 		FROM  `tabProject`
# 		LEFT JOIN `tabTask` ON `tabProject`.`name` = `tabTask`.`project`
	  

		
# 		WHERE  `tabProject`.`name`='{}' """.format(name), as_list=True)


# 	# query = frappe.db.count('Task', {'project': name})
# 	db = frappe.db.set_value('Project', name , 'task_count', query[0][0])

	
# 	try:
# 		return query[0][0],db
# 	except:
# 		frappe.throw("Please select the correct Project")

# @frappe.whitelist(allow_guest=True)
# def update_sle(name):
# 	console(name).log()
# 	doc = frappe.get_doc('Lead',name)
# 	console(doc.lead_name).log()
# 	# doc.db_set('valuation_rate', valuation_rate, commit=True, update_modified=False)
# 	# doc.db_set('qty_after_transaction', qty_after_transaction, commit=True, update_modified=False)
# 	# doc.db_set('stock_value', stock_value, commit=True, update_modified=False)
# 	# frappe.msgprint(cstr("Successfully updated"))

# 	# Use a query to fetch the items from the Sales Order
# 	items = frappe.db.sql("""SELECT item,total_cost,total_costing FROM `tabBOM Details` WHERE parent='{}'""".format(name), as_dict=True)

# 	# Create a new  document and set its fields
# 	sale_invoice = frappe.new_doc("Sales Invoice")
# 	sale_invoice.customer = doc.lead_name
# 	sale_invoice.lead_no = doc.name
# 	sale_invoice.posting_date = doc.date
# 	# sale_invoice.posting_time = doc.set_posting_time
# 	sale_invoice.due_date = doc.date
# 	sale_invoice.currency = 'PKR'
# 	sale_invoice.selling_price_list = 'Standard Selling'
# 	sale_invoice.debit_to = '1310 - Debtors - BM'
# 	sale_invoice.company = 'Booking Management'

# 	# Loop through the items and add them to the Delivery Note
# 	for item in items:

		
# 		sale_invoice.append("items", {
# 		"item_name":item.item,
# 		"description":item.item,
# 		"qty":item.qty,
# 		"uom":'Kg',
# 		"conversion_factor":'1',
# 		"rate": item.total_cost,
# 		"amount": item.total_costing,
# 		"income_account":'4110 - Sales - BM',
# 		"cost_center":'Main - BM' 
# 		                })

# 	# Save the Delivery Note
# 	console("before insert").log()
# 	sale_invoice.insert()
# 	console("after insert").log()
# 	sale_invoice.submit()
# 	console("after submit").log()

# 	# Return the name of the new Delivery Note document
# 	return sale_invoice.name

# # In this example, we first fetch the Sales Order document using its name. Then we use a SQL query to fetch the items from the Sales Order document. We then create a new Delivery Note document and set its fields using data from the Sales Order. Finally, we loop through the items and add them to the Delivery Note document. Once the Delivery Note is fully populated, we save it and return its name.

# # You can call this function with the name of a Sales Order document to create a new Delivery Note document based on its data.

# 	# return 'success'

# @frappe.whitelist(allow_guest=True)
# def payment(name):
# 	doc_lead = frappe.get_doc('Lead',name)
# 	console(doc_lead.name).log()
# 	console("Payment Entry me agya hun").log()
	

# 	#fetching sales invoice name according to lead no from sales invoice
# 	# doc = frappe.db.sql("""SELECT name from `tabSales Invoice` where lead_no='{}'""".format(name),as_dict=True)
# 	doc = frappe.db.sql("""SELECT name,due_date,total FROM `tabSales Invoice` WHERE lead_no='{}'""".format(name), as_dict=True)
# 	# doc = frappe.get_doc('Sales Invoice',lead_name= name)
# 	# get the last available Cancelled Task
# 	#doc = frappe.get_last_doc('Sales Invoice', filters={"lead_no": name})
# 	# console(doc.name).log()
# 	# Create a new  document and set its fields

# 	payment_entries = frappe.new_doc("Payment Entry")

	 
# 	payment_entries.payment_type = "Receive"
# 	# payment_entries.posting_date = 
# 	payment_entries.company = "Booking Management"
# 	payment_entries.mode_of_payment= "Cash"
# 	payment_entries.party_type = "Customer"
# 	payment_entries.party = doc_lead.lead_name
# 	payment_entries.party_name = doc_lead.lead_name
# 	payment_entries.target_exchange_rate = '1'

# 	payment_entries.paid_from = '1310 - Debtors - BM'
# 	payment_entries.paid_to = '1110 - Cash - BM'
# 	payment_entries.paid_to_account_currency = 'PKR'
# 	payment_entries.paid_from_account_currency = 'PKR'


# 	payment_entries.paid_amount = doc_lead.payments
# 	payment_entries.received_amount = doc_lead.payments

# 	# payment_entries.append("references", {
# 	# 	"reference_doctype": "Sales Invoice",
# 	# 	"reference_name": doc.name,
# 	# 	"due_date": doc_lead.date,
# 	# 	# "allocated_amount":

		
# 	# 	                })

# 	for d in doc:

# 		payment_entries.append("references", {
# 		"reference_doctype":'Sales Invoice',
# 		"reference_name":d.name,
# 		"due_date": d.due_date,
# 		"allocated_amount" : doc_lead.payments
# 		                })

# 	# Save the Delivery Note
# 	console("before insert").log()
# 	payment_entries.insert()
# 	payment_entries.submit()
# 	console("after insert").log()
# 	# sale_invoice.submit()
# 	# console("after submit").log()
# 	return payment_entries.name

	







# @frappe.whitelist(allow_guest=True)
# def create_sale(name):
# 	console("enter hgya bhai ").log()
# 	# doc = frappe.get_doc("Lead", name)

#     # Fetch the Sales Order document
# 	doc = frappe.get_doc("Lead", name)

#     # Use a query to fetch the items from the Sales Order
#     # items = frappe.db.sql("""
#     #     SELECT item_name,description,qty,rate
#     #     FROM `tabBOM Details`
#     #     WHERE parent=%s
#     # """, lead_name, as_dict=True)

#     # # Create a new Delivery Note document and set its fields
#     # sales_invoice = frappe.new_doc("Sales Invoice")
#     # sale_invoice.customer = lead.customer
#     # sale_invoice.posting_date = lead.posting_date
#     # sale_invoice.posting_time = lead.set_posting_time
#     # sale_invoice.due_date = lead.posting_date
#     # sale_invoice.currency = 'PKR'
#     # sale_invoice.selling_price_list = 'Standard Selling'
#     # sale_invoice.debit_to = '1310 - Debtors - BM'
#     # sale_invoice.company = 'Booking Management'

#     # # Loop through the items and add them to the Delivery Note
#     # for item in items:
#     # 	console("agya loop me").log()
#     #     sales_invoice.append("items", {
#     #     item_code:item.item_name,
#     #     description:'Biryani',
#     #     qty:'1',
#     #     uom:'Kg',
#     #     conversion_factor:'1',
#     #     rate:'12',
#     #     amount:'123',
#     #     income_account:'4110 - Sales - BM',
#     #     cost_center:'Main - BM' 
#     #                     })

#     # # Save the Delivery Note
#     # sales_invoice.insert()

#     # # Return the name of the new Delivery Note document
#     # return sales_invoice.name

# # In this example, we first fetch the Sales Order document using its name. Then we use a SQL query to fetch the items from the Sales Order document. We then create a new Delivery Note document and set its fields using data from the Sales Order. Finally, we loop through the items and add them to the Delivery Note document. Once the Delivery Note is fully populated, we save it and return its name.

# # You can call this function with the name of a Sales Order document to create a new Delivery Note document based on its data.
