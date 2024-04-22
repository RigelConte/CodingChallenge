import argparse
import csv
import json
import os
import sys
import xml.etree.ElementTree as ET

# Function to parse XML input file
def parse_xml(file_path):
    addresses = []

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        for ent in root.findall('ENTITY/ENT'):
            name = ent.find('NAME').text.strip()
            organization = ent.find('COMPANY').text.strip()
            street = ent.find('STREET').text.strip()
            city = ent.find('CITY').text.strip()
            state = ent.find('STATE').text.strip()
            postal_code = ent.find('POSTAL_CODE').text.strip()

            # Combine name and organization based on presence
            if name:
                entity = {'name': name}
            else:
                entity = {'organization': organization}

            entity.update({
                'street': street,
                'city': city,
                'state': state,
                'zip': postal_code
            })

            addresses.append(entity)

    except Exception as e:
        print(f"Error parsing XML file '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)

    return addresses


# Function to parse TSV input file
def parse_tsv(file_path):
    addresses = []

    try:
        with open(file_path, 'r', newline='') as file:
            reader = csv.DictReader(file, delimiter='\t')

            for row in reader:
                name = row.get('name', '').strip()
                organization = row.get('organization', '').strip()
                street = row.get('street', '').strip()
                city = row.get('city', '').strip()
                county = row.get('county', '').strip()
                state = row.get('state', '').strip()
                zip_code = row.get('zip', '').strip()

                # Construct address dictionary
                address = {}
                if name:
                    address['name'] = name
                else:
                    address['organization'] = organization
                address.update({
                    'street': street,
                    'city': city,
                    'state': state,
                    'zip': zip_code
                })
                if county:
                    address['county'] = county

                addresses.append(address)

    except Exception as e:
        print(f"Error parsing TSV file '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)

    return addresses

# Function to parse TXT input file
def parse_txt(file_path):
    data = []
    with open(file_path, 'r') as file:
        entry = {}
        for line in file:
            if line.strip() == '':
                if entry:
                    data.append(entry)
                    entry = {}
                continue
            if not entry.get('name'):
                entry['name'] = line.strip()
            elif not entry.get('street'):
                entry['street'] = line.strip()
            elif 'COUNTY' in line:
                entry['county'] = line.strip().replace('COUNTY', '').strip()
            else:
                parts = line.strip().split(', ')
                entry['city'] = parts[0]
                state_zip = parts[1].split(' ')
                entry['state'] = state_zip[0]
                entry['zip'] = state_zip[1] if len(state_zip) > 1 else ''
        if entry:
            data.append(entry)
    return data


# Function to validate input files
def validate_files(file_paths):
    valid_files = []
    invalid_files = []

    for file_path in file_paths:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            valid_files.append(file_path)
        else:
            invalid_files.append(file_path)

    return valid_files, invalid_files

# Main function
def main():
    parser = argparse.ArgumentParser(description='BankruptcyWatch Coding Challenge')
    parser.add_argument('files', metavar='FILE', type=str, nargs='+',
                        help='list of input files to parse')
    args = parser.parse_args()

    file_paths = args.files

    # Validate input files
    if not validate_files(file_paths):
       sys.exit(1)

    # Parse and combine addresses
    parsed_addresses = []
    for file_path in file_paths:
        if file_path.endswith('.xml'):
            parsed_addresses.extend(parse_xml(file_path))
        elif file_path.endswith('.tsv'):
            parsed_addresses.extend(parse_tsv(file_path))
        elif file_path.endswith('.txt'):
            parsed_addresses.extend(parse_txt(file_path))

    sorted_addresses = sorted(parsed_addresses, key=lambda x: x['zip'])
    print(json.dumps(sorted_addresses, indent=2))

if __name__ == '__main__':
    main()
