import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def fetch_subpages(domain):
    try:
        response = requests.get(domain, verify=False)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        subpages = []
        for link in soup.find_all('a', href=True):
            subpage_url = link['href']
            full_url = urljoin(domain, subpage_url)
            subpages.append(full_url)
        return subpages
    except requests.exceptions.RequestException as e:
        return []

def count_email_occurrences(subpage_url, email_to_search):
    try:
        response = requests.get(subpage_url, verify=False)
        html_content = response.text
        return html_content.count(email_to_search)
    except requests.exceptions.RequestException as e:
        return 0

def update_table(domain, email_to_search):
    subpages = fetch_subpages(domain)
    for subpage in subpages:
        email_count = count_email_occurrences(subpage, email_to_search)
        result_table.insert("", tk.END, values=(subpage, email_count))

def export_to_html(filename, data):
    with open(filename, 'w') as f:
        f.write('<html><head><title>Results</title></head><body>')
        f.write('<table border="1"><tr><th>Subpage</th><th>Email Count</th></tr>')
        for subpage, count in data:
            f.write(f'<tr><td><a href="{subpage}">{subpage}</a></td><td>{count}</td></tr>')
        f.write('</table></body></html>')

def export_to_csv(filename, data):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Subpage', 'Email Count'])
        for row in data:
            writer.writerow(row)

def export_results():
    file_type = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("HTML file", "*.html"), ("CSV file", "*.csv")])
    if file_type:
        data = [(result_table.set(item, 'Subpage'), result_table.set(item, 'Email Count')) for item in result_table.get_children()]
        if file_type.endswith('.html'):
            export_to_html(file_type, data)
        else:
            export_to_csv(file_type, data)
def update_status(status):
    status_label.config(text=status)

def search_and_update_status():
    domain = entry.get()
    email_to_search = email_entry.get()
    subpages = fetch_subpages(domain)
    
    for subpage in subpages:
        # Update status
        update_status(f"Searching subpage: {subpage}")
        
        # Update GUI
        root.update()
        
        # Search
        email_count = count_email_occurrences(subpage, email_to_search)
        result_table.insert("", tk.END, values=(subpage, email_count))
    
    # Search done
    update_status("Search done")


# GUI setup
root = tk.Tk()
root.title("Domain email counter")
root.geometry("1000x600")

# Domain and email entry in a top frame
top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X)

entry = tk.Entry(top_frame)
entry.insert(0, "Enter domain here (https://www.domain.com)")  # Default value
entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

email_entry = tk.Entry(top_frame)
email_entry.insert(0, "Enter email here (my@mail.com)")  # Default value
email_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

search_button = tk.Button(top_frame, text="Search", command=search_and_update_status)
search_button.pack(side=tk.RIGHT, padx=5)

# Result table
table_frame = tk.Frame(root)
table_frame.pack(fill=tk.BOTH, expand=True)

columns = ('Subpage', 'Email Count')
result_table = ttk.Treeview(table_frame, columns=columns, show='headings')
result_table.heading('Subpage', text='Subpage', anchor='w')
result_table.heading('Email Count', text='Email Count', anchor='w')

result_table.column('Subpage', width=600)  
result_table.column('Email Count', width=100)

result_table.pack(fill=tk.BOTH, expand=True)

status_label = tk.Label(root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W, width=100)
status_label.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X)

export_button = tk.Button(root, text="Export", command=export_results)
export_button.pack(pady=5)

root.mainloop()
