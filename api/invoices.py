def post_invoices(files):
    # Hardcoded single transaction
    try:
        file_key = list(files.keys())[0]
        sample_file = files[file_key]
        sample_extraction = sample_file['df']
        sample_transaction = sample_extraction[90]
        print(sample_transaction)

        result = single_invoice(sample_transaction)
        if result:
            return True
    
        return False
    
    except Exception as e:
        print(e)
        return False


def single_invoice(transaction):
    
    invoice = {
    "Line": [{
        "DetailType": "SalesItemLineDetail",
        "Amount": 100.0,
        "SalesItemLineDetail": {
            "ItemRef": {
                "name": "Concrete",
                "value": "3"
            }
        }
    }],
    "CustomerRef": {
        "value": "1"
        }
    }

    return True
