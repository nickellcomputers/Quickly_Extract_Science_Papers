import sqlite3
import csv
import os

# Database file path
database = "D:\\Users\\Gong Creation\\Desktop\\Global Desktop\\OneDrive\\Programming\\Thought Bounce\\Project1.NET\\bin\\newthoughts.db"

import sqlite3

def create_google_contacts_table():
    conn = sqlite3.connect(database)
    c = conn.cursor()

    # Creating table
    c.execute('''
        CREATE TABLE IF NOT EXISTS ImportGoogleContacts(
            GoogleContactID INTEGER PRIMARY KEY,
            Name TEXT,
            GivenName TEXT,
            AdditionalName TEXT,
            FamilyName TEXT,
            YomiName TEXT,
            GivenNameYomi TEXT,
            AdditionalNameYomi TEXT,
            FamilyNameYomi TEXT,
            NamePrefix TEXT,
            Initials TEXT,
            Nickname TEXT,
            ShortName TEXT,
            MaidenName TEXT,
            Birthday TEXT,
            Gender TEXT,
            Location TEXT,
            BillingInformation TEXT,
            Directory TEXT,
            Mileage TEXT,
            Occupation TEXT,
            Hobby TEXT,
            Sensitivity TEXT,
            Priority TEXT,
            Subject TEXT,
            Notes TEXT,
            Language TEXT,
            Photo TEXT,
            GroupMembership TEXT,
            Email1Type TEXT,
            Email1Value TEXT,
            Email2Type TEXT,
            Email2Value TEXT,
            Phone1Type TEXT,
            Phone1Value TEXT,
            Phone2Type TEXT,
            Phone2Value TEXT,
            Address1Type TEXT,
            Address1Formatted TEXT,
            Address1Street TEXT,
            Address1City TEXT,
            Address1POBox TEXT,
            Address1Region TEXT,
            Address1Country TEXT,
            Address1ExtendedAddress TEXT,
            Address2Type TEXT,
            Address2Formatted TEXT,
            Address2Street TEXT,
            Address2City TEXT,
            Address2POBox TEXT,
            Address2Region TEXT,
            Address2Country TEXT,
            Address2ExtendedAddress TEXT,
            Organization1Type TEXT,
            Organization1Name TEXT,
            Organization1YomiName TEXT,
            Organization1Title TEXT,
            Organization1Department TEXT,
            Organization1Symbol TEXT,
            Organization1Location TEXT,
            Organization1JobDescription TEXT,
            Website1Type TEXT,
            Website1Value TEXT,
            Relationship TEXT
        )
    ''')

    conn.commit()
    conn.close()




def get_contact_data_as_csv_string(relationship):
    # Create a database connection
    conn = sqlite3.connect(database)
    c = conn.cursor()

    # Parameterize the relationship input to avoid SQL injection
    params = (relationship, )

    # Select FirstName, LastName, and Relationship fields from the Contacts table where Relationship matches the input
    c.execute("SELECT FirstName, LastName, Relationship FROM MainContacts WHERE Relationship = ?", params)
    rows = c.fetchall()

    # Convert the rows to a CSV string
    csv_string = ""
    for row in rows:
        csv_string += ' '.join([str(item) for item in row]) + '\n'

    # Close the connection
    conn.close()

    # Return the CSV string
    return csv_string



