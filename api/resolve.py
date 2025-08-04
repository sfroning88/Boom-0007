def resolve_customers(invoices_extracted):
    import re
    import concurrent.futures
    from tqdm import tqdm

    from api.retrieve import get_customers
    customers_pre = get_customers()
    customers_post = customers_pre['Customer']

    customers_existing = []
    for customer in customers_post:
        customers_existing.append(customer['DisplayName'])
    if len(customers_existing) == 0:
        return invoices_extracted

    print(f"Customers len = {len(customers_existing)}")

    customers_new = []
    for customer_object in list(invoices_extracted.values()):
        customers_new.append(customer_object['Name'])
    customers_new = list(set(customers_new))
    print(f"Found {len(customers_new)} new customers to add")

    # dictionary for rename mappings
    customer_mapping = {}

    # map new customers to closest match existing
    for invoice_name in customers_new:
        for customer_name in customers_existing:
            # Check for exact match to skip
            if re.match(invoice_name, customer_name, re.IGNORECASE):
                customers_new.remove(invoice_name)
                break

           # Check for partial match to replace
            if re.search(invoice_name, customer_name, re.IGNORECASE):
                # if match found, add mapping of (old): (to replace with)
                customer_mapping[invoice_name] = customer_name
                customers_new.remove(invoice_name)
                break

            elif re.search(customer_name, invoice_name, re.IGNORECASE):
                # if match found, add mapping of (old): (to replace with)
                customer_mapping[invoice_name] = customer_name
                customers_new.remove(invoice_name)
                break

    print(f"Found these mappings: {customer_mapping}")
    for customer_object in list(invoices_extracted.values()):
        if customer_object['Name'] in list(customer_mapping.keys()):
            print(f"Replacing {customer_object['Name']} with {customer_mapping[customer_object['Name']]}")
            customer_object['Name'] = customer_mapping[customer_object['Name']]
    
    print(f"Remaining new customers to add: {len(customers_new)}")

    customers_added = []
    for invoice_name in customers_new:
        # Create dummy customer object and add to database
        dummy_customer = {
            'Customer': invoice_name,
            'Bill To': '',
            'Primary Contact': '',
            'Main Phone': '',
            'Fax': '',
            'Balance Total': 0.0
        }
        customers_added.append(dummy_customer)

    # Concurrently post all customers from customers
    from api.customers import customer_threadsafe
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        list(tqdm(executor.map(customer_threadsafe, customers_added), total=len(customers_added)))

    return invoices_extracted

def resolve_cust_ids(invoices_extracted):
    from api.retrieve import get_customers
    customers_pre = get_customers()
    customers_post = customers_pre['Customer']

    # pull QBO id from customers
    ids_mapping = {}
    for customer in customers_post:
        ids_mapping[customer['DisplayName']] = customer['Id']
    if len(ids_mapping.values()) != len(ids_mapping.keys()):
        print("Customers does not equal ids, some other error occured")
        return invoices_extracted
    if len(list(ids_mapping.values())) == 0:
        return invoices_extracted

    print(f"Customers/Ids len = {len(list(ids_mapping.values()))}")

    # assign each invoice the corresponding id
    for invoice_object in list(invoices_extracted.values()):
        invoice_object['Id'] = ids_mapping[invoice_object['Name']]

    return invoices_extracted

def resolve_vendors(bills_extracted):
    import re
    import concurrent.futures
    from tqdm import tqdm

    from api.retrieve import get_vendors
    vendors_pre = get_vendors()
    vendors_post = vendors_pre['Vendor']

    vendors_existing = []
    for vendor in vendors_post:
        vendors_existing.append(vendor['DisplayName'])
    if len(vendors_existing) == 0:
        return bills_extracted

    print(f"Vendors len = {len(vendors_existing)}")

    vendors_new = []
    for bill_object in list(bills_extracted.values()):
        vendors_new.append(bill_object['Name'])
    vendors_new = list(set(vendors_new))
    print(f"Found {len(vendors_new)} new vendors to add")

    # dictionary for rename mappings
    vendor_mapping = {}

    # map new customers to closest match existing
    for bill_name in vendors_new:
        for vendor_name in vendors_existing:
            # Check for exact match to skip
            if re.match(bill_name, vendor_name, re.IGNORECASE):
                vendors_new.remove(bill_name)
                break

           # Check for partial match to replace
            if re.search(bill_name, vendor_name, re.IGNORECASE):
                # if match found, add mapping of (old): (to replace with)
                vendor_mapping[bill_name] = vendor_name
                vendors_new.remove(bill_name)
                break

            elif re.search(vendor_name, bill_name, re.IGNORECASE):
                # if match found, add mapping of (old): (to replace with)
                vendor_mapping[bill_name] = vendor_name
                vendors_new.remove(bill_name)
                break

    print(f"Found these mappings: {vendor_mapping}")
    for vendor_object in list(bills_extracted.values()):
        if vendor_object['Name'] in list(vendor_mapping.keys()):
            print(f"Replacing {vendor_object['Name']} with {vendor_mapping[vendor_object['Name']]}")
            vendor_object['Name'] = vendor_mapping[vendor_object['Name']]
    
    print(f"Remaining new vendors to add: {len(vendors_new)}")

    vendors_added = []
    for bill_name in vendors_new:
        # Create dummy vendor object and add to database
        dummy_vendor = {
            'Vendor': bill_name,
            'Bill To': '',
            'Primary Contact': '',
            'Main Phone': '',
            'Fax': '',
            'Balance Total': 0.0
        }
        vendors_added.append(dummy_vendor)

    # Concurrently post all customers from customers
    from api.vendors import vendor_threadsafe
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        list(tqdm(executor.map(vendor_threadsafe, vendors_added), total=len(vendors_added)))

    return bills_extracted

def resolve_vend_ids(bills_extracted):
    from api.retrieve import get_vendors
    vendors_pre = get_vendors()
    vendors_post = vendors_pre['Vendor']

    # pull QBO id from customers
    ids_mapping = {}
    for vendor in vendors_post:
        ids_mapping[vendor['DisplayName']] = vendor['Id']
    if len(ids_mapping.values()) != len(ids_mapping.keys()):
        print("Vendors does not equal ids, some other error occured")
        return bills_extracted
    if len(list(ids_mapping.values())) == 0:
        return bills_extracted

    print(f"Vendors/Ids len = {len(list(ids_mapping.values()))}")

    # assign each invoice the corresponding id
    for bill_object in list(bills_extracted.values()):
        bill_object['Id'] = ids_mapping[bill_object['Name']]

    return bills_extracted
