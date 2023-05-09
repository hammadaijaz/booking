import frappe
from frappe import _
from console import console
from frappe.model.mapper import get_mapped_doc
import frappe
from frappe.utils import cstr, getdate
import json
from frappe.utils.background_jobs import enqueue
from frappe.utils import now_datetime


@frappe.whitelist()
def no_of_task(name):

	query = frappe.db.sql(""" 
		SELECT 
		
	    COUNT(`tabTask`.`name`) as "No. of Tasks"


		FROM  `tabProject`
		LEFT JOIN `tabTask` ON `tabProject`.`name` = `tabTask`.`project`
	  

		
		WHERE  `tabProject`.`name`='{}' """.format(name), as_list=True)


	# query = frappe.db.count('Task', {'project': name})
	db = frappe.db.set_value('Project', name , 'task_count', query[0][0])

	
	try:
		return query[0][0],db
	except:
		frappe.throw("Please select the correct Project")

@frappe.whitelist(allow_guest=True)
def update_sle(name):
	console(name).log()
	doc = frappe.get_doc('Lead',name)
	console(doc.lead_name).log()
	# doc.db_set('valuation_rate', valuation_rate, commit=True, update_modified=False)
	# doc.db_set('qty_after_transaction', qty_after_transaction, commit=True, update_modified=False)
	# doc.db_set('stock_value', stock_value, commit=True, update_modified=False)
	# frappe.msgprint(cstr("Successfully updated"))

	# Use a query to fetch the items from the BOM DETAILS CHILD TABLE
	items = frappe.db.sql("""SELECT item,rate,qty,bom_management_cost,total_cost,total_costing FROM `tabBOM Details` WHERE parent='{}'""".format(name), as_dict=True)

	# Use a query to fetch the items from the ADDITIONAL ITEM CHILD TABLE
	add_items = frappe.db.sql("""SELECT item,valuation_rate FROM `tabAdditional Items` WHERE parent='{}'""".format(name), as_dict=True)


	# Create a new  document and set its fields
	sale_invoice = frappe.new_doc("Sales Invoice")
	sale_invoice.customer = doc.lead_name
	sale_invoice.lead_no = doc.name
	sale_invoice.posting_date = doc.date
	# sale_invoice.posting_time = doc.set_posting_time
	sale_invoice.due_date = doc.date
	sale_invoice.currency = 'PKR'
	sale_invoice.selling_price_list = 'Standard Selling'
	sale_invoice.debit_to = '1310 - Debtors - BM'
	sale_invoice.company = 'Booking Management'

	# Loop through the items and add them to the Delivery Note
	for item in items:

		
		sale_invoice.append("items", {
		"item_name":item.item,
		"description":item.item,
		"qty":item.qty,
		"uom":'Kg',
		"conversion_factor":'1',
		"rate": item.rate,
		"amount": item.total_costing,
		"income_account":'4110 - Sales - BM',
		"cost_center":'Main - BM' 
		                })


	for add in add_items:
		sale_invoice.append("items",{
			"item_name":add.item,
			"description":add.item,
			"qty":'1',
			"uom":'Nos',
			"conversion_factor":'1',
			"rate":add.valuation_rate,
			"income_account":'4110 - Sales - BM',
			"cost_center":'Main - BM' 
			})


	# Save the Delivery Note
	console("before insert").log()
	sale_invoice.insert()
	console("after insert").log()
	sale_invoice.submit()
	console("after submit").log()

	# #Working on lead doc type to update lead color in main lead form Blue to green
	# doc_lead = frappe.get_doc('Lead',name)

	# doc_lead.color = '#29CD42'
	# doc_lead.insert()

	db = frappe.db.set_value('Lead', name , 'color', '#29CD42')


	# Return the name of the new Delivery Note document
	return sale_invoice.name

# In this example, we first fetch the Sales Order document using its name. Then we use a SQL query to fetch the items from the Sales Order document. We then create a new Delivery Note document and set its fields using data from the Sales Order. Finally, we loop through the items and add them to the Delivery Note document. Once the Delivery Note is fully populated, we save it and return its name.

# You can call this function with the name of a Sales Order document to create a new Delivery Note document based on its data.

	# return 'success'

@frappe.whitelist(allow_guest=True)
def payment(name):
	doc_lead = frappe.get_doc('Lead',name)
	console(doc_lead.name).log()
	console("Payment Entry me agya hun").log()
	

	#fetching sales invoice name according to lead no from sales invoice
	# doc = frappe.db.sql("""SELECT name from `tabSales Invoice` where lead_no='{}'""".format(name),as_dict=True)
	doc = frappe.db.sql("""SELECT name,due_date,total FROM `tabSales Invoice` WHERE lead_no='{}'""".format(name), as_dict=True)
	# doc = frappe.get_doc('Sales Invoice',lead_name= name)
	# get the last available Cancelled Task
	#doc = frappe.get_last_doc('Sales Invoice', filters={"lead_no": name})
	# console(doc.name).log()
	# Create a new  document and set its fields

	payment_entries = frappe.new_doc("Payment Entry")

	 
	payment_entries.payment_type = "Receive"
	# payment_entries.posting_date = 
	payment_entries.company = "Booking Management"
	payment_entries.mode_of_payment= "Cash"
	payment_entries.party_type = "Customer"
	payment_entries.party = doc_lead.lead_name
	payment_entries.party_name = doc_lead.lead_name
	payment_entries.target_exchange_rate = '1'

	payment_entries.paid_from = '1310 - Debtors - BM'
	payment_entries.paid_to = '1110 - Cash - BM'
	payment_entries.paid_to_account_currency = 'PKR'
	payment_entries.paid_from_account_currency = 'PKR'


	payment_entries.paid_amount = doc_lead.payments
	payment_entries.received_amount = doc_lead.payments

	# payment_entries.append("references", {
	# 	"reference_doctype": "Sales Invoice",
	# 	"reference_name": doc.name,
	# 	"due_date": doc_lead.date,
	# 	# "allocated_amount":

		
	# 	                })

	for d in doc:

		payment_entries.append("references", {
		"reference_doctype":'Sales Invoice',
		"reference_name":d.name,
		"due_date": d.due_date,
		"allocated_amount" : doc_lead.payments
		                })

	# Save the Delivery Note
	console("before insert").log()
	payment_entries.insert()
	payment_entries.submit()
	console("after insert").log()
	 # Reload the target document
	# console(doc.name).log()
	# frappe.reload_doc('Sales Invoice', 'ACC-SINV-2023-00072')

	# sale_invoice.submit()
	# console("after submit").log()
	return payment_entries.name

	
@frappe.whitelist(allow_guest=True)
def workorder(name):
	console(name).log()
	console("enter in workorder").log()
	doc_lead = frappe.get_doc('Lead',name)
	console(doc_lead.lead_name).log()

	# fetching BOM NO from lead bom child table (BOM-Biryani-002 / BOM-Kheer-001 )
	lead_bom = frappe.db.sql("""SELECT bom,qty,parent FROM `tabBOM Details` WHERE parent='{}'""".format(name), as_dict=True)

	#once Bom no has been fetched then calling its further items from Main Bom Form
	for bom_item in lead_bom:
		console(bom_item).log()
		bom_no  = bom_item.bom
		console(bom_no).log()
		bom_qty = bom_item.qty
		console(bom_qty).log()
		lead_no = bom_item.parent
		console("end of work order").log()
		create_work_order(bom_no,bom_qty,lead_no)







def create_work_order(bom_no,bom_qty,lead_no):
	
	current_datetime = now_datetime()
	console(current_datetime).log()
	console(bom_no).log()
	console(bom_qty).log()
	console(lead_no).log()



	# #fetching values recipe items against bom no from main bom table (Rice/sugar)
	doc = frappe.db.sql("""SELECT * FROM `tabBOM Item` WHERE parent='{}'""".format(bom_no), as_dict=True)

	# op_doc = frappe.get_doc('BOM Operation',bom_no)
	op_doc =  frappe.db.sql("""SELECT * FROM `tabBOM Operation` WHERE parent='{}'""".format(bom_no), as_dict=True)


	bom = frappe.get_doc('BOM',bom_no)
	# bom = frappe.db.sql("""SELECT item,item_name FROM `tabBOM` WHERE name='{}'""".format(bom_no))
	console(bom.item).log()
	console(bom.item_name).log()
	console("after bom").log()

	# bom = frappe.get_doc('Bom',name)

    

	# # Create a new  document and set its fields
	work_order = frappe.new_doc("Work Order")

	work_order.production_item = bom.item
	work_order.bom_no = bom.name
	work_order.comapany = bom.company
	work_order.qty = bom_qty
	work_order.lead_no = lead_no
	work_order.use_multi_level_bom = '1'
	work_order.update_consumed_material_cost_in_project = '1'
	work_order.source_warehouse = 'Stores - BM'
	work_order.wip_warehouse = 'Work In Progress - BM'
	work_order.fg_warehouse = 'Finished Goods - BM'
	work_order.planned_start_date = current_datetime

	for items in doc:
		work_order.append("required_items",{
			"item_code" : items.item_code,
			 "item_name" : items.item_name,
			 "source_warehouse" : "Stores - BM",
			 "description" : items.description,
			 "include_item_in_manufacturing" : '1',
			})

	for op in op_doc:
		work_order.append("operations",{
			"operation" : op.operation,
			"bom" : op.parent,
			"workstation" : op.workstation,
			"completed_qty": bom_qty,
			"description" : op.description,
			"time_in_mins" : op.time_in_mins,

		})



	console("before insert workorder").log()
	work_order.insert()
	# work_order.submit()
	console("after insert workorder").log()

	return work_order.name
	


@frappe.whitelist(allow_guest=True)
def create_stock_entry(name):
	console("enter in stock entry method from py script").log()
	console(name).log()
	console("Passed Workorder name from scipt in method").log()

	# #fetching values from Workrder PARENT for creation of Stock Entry 
	# doc = frappe.db.sql("""SELECT * FROM `tabWorkOrder` WHERE name='{}'""".format(name), as_dict=True)
	work_order_doc = frappe.get_doc("Work Order" , name)

	# fetching ITEMS from BOM to create a stock entry
	bom_item = frappe.db.sql("""SELECT * FROM `tabBOM Item` WHERE parent='{}'""".format(work_order_doc.bom_no), as_dict=True)



	stock_entry_doc = frappe.new_doc("Stock Entry")

	#entring values in stock entry doc

	stock_entry_doc.stock_entry_type = 'Material Transfer for Manufacture'
	stock_entry_doc.company = "Booking Management"
	stock_entry_doc.work_order = work_order_doc.name
	stock_entry_doc.from_bom = '1'
	stock_entry_doc.bom_no = work_order_doc.bom_no
	stock_entry_doc.use_multi_level_bom = '1'
	stock_entry_doc.fg_completed_qty = work_order_doc.qty
	stock_entry_doc.to_warehouse = 'Work In Progress - BM'
	stock_entry_doc.is_openning = 'No'

	for item in bom_item:
		stock_entry_doc.append("items",{

		"s_warehouse" : 'Stores - BM',
		"t_warehouse" : 'Work In Progress - BM',
		"item_code" : item.item_code,
		"qty" : work_order_doc.qty,  #needs to multiply with bom qty to find actual qty
		"uom" : item.uom,
		"stock_uom" : item.stock_uom,
		"transfer_qty" : work_order_doc.qty,
		"conversion_factor" : item.conversion_factor,
		"basic_rate" : item.rate,
		"expense_account" : '5119 - Stock Adjustment - BM',
		"cost_center" : 'Main - BM'

		})

	console("reached insert method").log()
	stock_entry_doc.insert()
	stock_entry_doc.submit()
	console("stock insert").log()

	return stock_entry_doc.name

@frappe.whitelist(allow_guest=True)
def update_jobcard(name,employee):
	console("enter in update jobcard method").log()
	console("name").log()
	console(name).log()
	console("employee").log()
	console(employee).log()
	
	doc = frappe.db.sql("""SELECT name FROM `tabJob Card` WHERE work_order='{}'""".format(name), as_dict=True)
	# time_details = frappe.db.sql("""SELECT * FROM `tabJob Card` WHERE parent='{}'""".format(doc.name), as_dict=True)

	# doc = frappe.get_doc({"doctype": "Job Card","work_order":"MFG-WO-2023-00038"})
	# doc = frappe.get_doc(doctype='Job Card', work_order='MFG-WO-2023-00038')
	for i in doc:
		console("doc").log()
		console(employee).log()
		console(i.name).log()
		i.job_assigned = employee
		console("asig member").log()
		console(i.job_assigned).log()
		db = frappe.db.set_value('Job Card',i.name , 'job_assigned', employee)

		
	# doc.insert()

	# time_detail = doc.get("time_logs")

	# console(time_detail).log()
	# my_field = doc.get("employee")
	# console(my_field).log()
	# my_field.append(employee)
	# db = frappe.db.set_value('Job Card',doc.name , 'employee', employee)
	# for i in range(len(time_detail)):
	# 	time_detail[0].completed_qty = '3'

	# console("save se pehle").log()
	

	return doc.name



@frappe.whitelist(allow_guest=True)
def create_sale(name):
	console("enter hgya bhai ").log()
	# doc = frappe.get_doc("Lead", name)

    # Fetch the Sales Order document
	doc = frappe.get_doc("Lead", name)

    # Use a query to fetch the items from the Sales Order
    # items = frappe.db.sql("""
    #     SELECT item_name,description,qty,rate
    #     FROM `tabBOM Details`
    #     WHERE parent=%s
    # """, lead_name, as_dict=True)

    # # Create a new Delivery Note document and set its fields
    # sales_invoice = frappe.new_doc("Sales Invoice")
    # sale_invoice.customer = lead.customer
    # sale_invoice.posting_date = lead.posting_date
    # sale_invoice.posting_time = lead.set_posting_time
    # sale_invoice.due_date = lead.posting_date
    # sale_invoice.currency = 'PKR'
    # sale_invoice.selling_price_list = 'Standard Selling'
    # sale_invoice.debit_to = '1310 - Debtors - BM'
    # sale_invoice.company = 'Booking Management'

    # # Loop through the items and add them to the Delivery Note
    # for item in items:
    # 	console("agya loop me").log()
    #     sales_invoice.append("items", {
    #     item_code:item.item_name,
    #     description:'Biryani',
    #     qty:'1',
    #     uom:'Kg',
    #     conversion_factor:'1',
    #     rate:'12',
    #     amount:'123',
    #     income_account:'4110 - Sales - BM',
    #     cost_center:'Main - BM' 
    #                     })

    # # Save the Delivery Note
    # sales_invoice.insert()

    # # Return the name of the new Delivery Note document
    # return sales_invoice.name

# In this example, we first fetch the Sales Order document using its name. Then we use a SQL query to fetch the items from the Sales Order document. We then create a new Delivery Note document and set its fields using data from the Sales Order. Finally, we loop through the items and add them to the Delivery Note document. Once the Delivery Note is fully populated, we save it and return its name.

# You can call this function with the name of a Sales Order document to create a new Delivery Note document based on its data.
