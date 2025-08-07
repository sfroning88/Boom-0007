def resolve_customers(invoices_extracted):
    import concurrent.futures
    from tqdm import tqdm

    from api.retrieve import get_database
    customers_pre = get_database(query_mode="Customer")

    if customers_pre is None or 'Customer' not in list(customers_pre.keys()):
        print("WARNING: Please upload Customers to QBO before posting invoices")
        return None

    customers_post = customers_pre['Customer']

    # pull all existing customers
    customers_existing = []
    for customer in customers_post:
        customers_existing.append(customer['DisplayName'])
    if len(customers_existing) == 0:
        return invoices_extracted

    print(f"CHECKPOINT: Found {len(customers_existing)} existing Customers")

    customers_new = []
    for customer_object in list(invoices_extracted.values()):
        customers_new.append(customer_object['Name'])
    customers_new = list(set(customers_new))
    customers_new.sort()

    # remove any duplicate customers
    for invoice_name in customers_new:
        if invoice_name in customers_existing:
            customers_new.remove(invoice_name)

    customers_added = []
    for invoice_name in customers_new:
        # Create dummy customer object and add to database
        dummy_customer = {
            "Customer": invoice_name,
            "Primary Contact": "",
            "Main Phone": "",
            "Bill To": "",
            "Balance Total": 0.0
        }

        customers_added.append(dummy_customer)

    print(f"CHECKPOINT: Found {len(customers_added)} new Customers to add")

    # Concurrently post all customers from customers
    from api.customers import customer_threadsafe
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        list(tqdm(executor.map(customer_threadsafe, customers_added), total=len(customers_added)))

    return invoices_extracted

def resolve_cust_ids(invoices_extracted):
    from api.retrieve import get_database
    customers_pre = get_database(query_mode="Customer")
    customers_post = customers_pre['Customer']

    # pull QBO id from customers
    ids_mapping = {}
    for customer in customers_post:
        ids_mapping[customer['DisplayName']] = customer['Id']
    if len(ids_mapping.values()) != len(ids_mapping.keys()):
        print("ERROR: Customers does not equal ids, some other error occured")
        return invoices_extracted
    if len(list(ids_mapping.values())) == 0:
        return invoices_extracted

    print(f"CHECKPOINT: Found {len(list(ids_mapping.values()))} existing Ids")

    # assign each invoice the corresponding id
    for invoice_object in list(invoices_extracted.values()):
        if invoice_object['Name'] in list(ids_mapping.keys()):
            invoice_object['Id'] = ids_mapping[invoice_object['Name']]

    return invoices_extracted

def resolve_vendors(bills_extracted):
    import concurrent.futures
    from tqdm import tqdm

    from api.retrieve import get_database
    vendors_pre = get_database(query_mode="Vendor")
    if vendors_pre is None or 'Vendor' not in list(vendors_pre.keys()):
        print("WARNING: Please upload Vendors to QBO before posting bills")
        return None
    
    vendors_post = vendors_pre['Vendor']

    vendors_existing = []
    for vendor in vendors_post:
        vendors_existing.append(vendor['DisplayName'])
    if len(vendors_existing) == 0:
        return bills_extracted

    print(f"CHECKPOINT: Found {len(vendors_existing)} existing Vendors")

    vendors_new = []
    for bill_object in list(bills_extracted.values()):
        vendors_new.append(bill_object['Name'])
    vendors_new = list(set(vendors_new))

    # remove any duplicate vendors
    for bill_name in vendors_new:
        if bill_name in vendors_existing:
            vendors_new.remove(bill_name)

    vendors_added = []
    for bill_name in vendors_new:
        # Create dummy vendor object and add to database
        dummy_vendor = {
            "Vendor": bill_name,
            "Account #": "",
            "Primary Contact": "",
            "Main Phone": "",
            "Bill From": "",
            "Balance Total": 0.0
        }
        vendors_added.append(dummy_vendor)

    print(f"CHECKPOINT: Found {len(vendors_added)} new Vendors to add")

    # Concurrently post all vendors from vendors
    from api.vendors import vendor_threadsafe
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        list(tqdm(executor.map(vendor_threadsafe, vendors_added), total=len(vendors_added)))

    return bills_extracted

def resolve_vend_ids(bills_extracted):
    from api.retrieve import get_database
    vendors_pre = get_database(query_mode="Vendor")
    vendors_post = vendors_pre['Vendor']

    # pull QBO id from customers
    ids_mapping = {}
    for vendor in vendors_post:
        ids_mapping[vendor['DisplayName']] = vendor['Id']
    if len(ids_mapping.values()) != len(ids_mapping.keys()):
        print("ERROR: Vendors does not equal ids, some other error occured")
        return bills_extracted
    if len(list(ids_mapping.values())) == 0:
        return bills_extracted

    print(f"CHECKPOINT: Found {len(list(ids_mapping.values()))} existing Ids")

    # assign each invoice the corresponding id
    for bill_object in list(bills_extracted.values()):
        if bill_object['Name'] in list(ids_mapping.keys()):
            bill_object['Id'] = ids_mapping[bill_object['Name']]

    return bills_extracted
