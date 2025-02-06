from flask import Flask, render_template, request, send_file
import sqlite3
from fpdf import FPDF

app = Flask(__name__)

@app.route('/')
def index():
    try:
        # Connect to the database and fetch equipment details
        conn = sqlite3.connect('equipment.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM equipment")
        equipment = cursor.fetchall()
        conn.close()

        # Pass the equipment data to the template
        return render_template('index.html', equipment=equipment)
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"

@app.route('/generate_bill', methods=['POST'])
def generate_bill():
    try:
        # Get selected items and quantities from the form
        selected_items = request.form.getlist('selected_items')
        quantities = request.form.getlist('quantity')

        if not selected_items:
            return "No items selected for rent."

        # Use parameterized queries to prevent SQL injection
        conn = sqlite3.connect('equipment.db')
        cursor = conn.cursor()
        placeholders = ','.join(['?'] * len(selected_items))
        cursor.execute(f"SELECT id, name, rental_price FROM equipment WHERE id IN ({placeholders})", tuple(selected_items))
        items = cursor.fetchall()
        conn.close()

        items_with_quantity = []
        total_cost = 0

        # Calculate item totals and overall cost
        for i, item in enumerate(items):
            item_id, name, price = item
            quantity = int(quantities[i])
            subtotal = price * quantity
            total_cost += subtotal
            items_with_quantity.append({
                'name': name,
                'quantity': quantity,
                'price': price,
                'subtotal': subtotal
            })

        # Render the bill with items, quantities, and total cost
        return render_template('bill.html', items=items_with_quantity, total_cost=total_cost)

    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    try:
        # Fetch the selected items, quantities, and total cost from the form
        selected_items = request.form.getlist('item_names')
        quantities = request.form.getlist('item_quantities')
        prices = request.form.getlist('item_prices')
        subtotals = request.form.getlist('item_subtotals')
        total_cost = request.form['total_cost']

        # Column widths
        col_widths = [60, 30, 30, 40]
        table_width = sum(col_widths)
        page_width = 210  # A4 page width in mm
        x_margin = (page_width - table_width) / 2  # Calculate margin for centering

        # Create the PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Use a Unicode-compatible font like DejaVu Sans
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        
        # Set the font for NF Events with a larger size
        pdf.set_font("DejaVu", size=18)
        pdf.cell(200, 10, txt="NF Events", ln=True, align='C')

        # Set font size back to normal for the following lines
        pdf.set_font("DejaVu", size=12)

        # Add the location below the heading with reduced gap and centered
        pdf.cell(200, 10, txt="Parambil Kadavu, Calicut, Kerala", ln=True, align='C')

        # Add contact number without any gap below the location
        pdf.cell(200, 10, txt="Contact: 9961087014, 7012759471", ln=True, align='C')

        # Add a separation line below the contact information
        line_y = pdf.get_y() + 2  # Position the line slightly below the text
        pdf.line(10, line_y, 200, line_y)  # Draw a horizontal line from x=10 to x=200

        # Add a gap before the table
        pdf.ln(10)

        # Add table headers (centered)
        pdf.set_x(x_margin)  # Align to center
        pdf.cell(col_widths[0], 10, txt="Equipment Name", border=1, align='C')
        pdf.cell(col_widths[1], 10, txt="Quantity", border=1, align='C')
        pdf.cell(col_widths[2], 10, txt="Price (₹)", border=1, align='C')
        pdf.cell(col_widths[3], 10, txt="Subtotal (₹)", border=1, align='C')
        pdf.ln()

        # Add table rows (centered)
        for i in range(len(selected_items)):
            pdf.set_x(x_margin)  # Align to center for each row
            pdf.cell(col_widths[0], 10, txt=selected_items[i], border=1, align='C')
            pdf.cell(col_widths[1], 10, txt=quantities[i], border=1, align='C')
            pdf.cell(col_widths[2], 10, txt=prices[i], border=1, align='C')
            pdf.cell(col_widths[3], 10, txt=subtotals[i], border=1, align='C')
            pdf.ln()

        # Add total cost (centered)
        pdf.ln(10)
        pdf.set_x(x_margin)
        pdf.cell(table_width, 10, txt=f"Total Cost: ₹{total_cost}", border=1, align='C')

        # Save the PDF
        pdf_path = "generated_bill.pdf"
        pdf.output(pdf_path)

        # Serve the PDF to the user
        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"

if __name__ == "__main__":
    app.run(debug=True, port=5001)
