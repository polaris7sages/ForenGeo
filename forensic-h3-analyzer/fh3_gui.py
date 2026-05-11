import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import folium
import webbrowser
import tempfile
import os
from forensic_h3_fixed import ForensicH3Analyzer
import pandas as pd

class FH3GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FH3 Advanced Forensic Analyzer")
        self.root.geometry("1200x800")

        self.indexer = None
        self.db_path = tk.StringVar(value=".fh3.db")

        self.setup_ui()

    def setup_ui(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load DB", command=self.load_db)
        file_menu.add_command(label="Init New DB", command=self.init_db)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="Hotspots", command=self.show_hotspots)
        analysis_menu.add_command(label="Anomalies", command=self.show_anomalies)
        analysis_menu.add_command(label="Movement Patterns", command=self.show_patterns)
        analysis_menu.add_command(label="Privacy Assessment", command=self.show_privacy)

        osint_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="OSINT", menu=osint_menu)
        osint_menu.add_command(label="Reverse Geocode", command=self.reverse_geocode)
        osint_menu.add_command(label="POI Search", command=self.poi_search)
        osint_menu.add_command(label="Geocode Address", command=self.geocode_address)

        export_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Export", menu=export_menu)
        export_menu.add_command(label="Interactive Map", command=self.create_map)
        export_menu.add_command(label="KML Export", command=self.export_kml)
        export_menu.add_command(label="CSV Export", command=self.export_csv)

        # Toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill='x', padx=5, pady=5)

        ttk.Button(toolbar, text="📁 Add Files", command=self.add_files).pack(side='left')
        ttk.Button(toolbar, text="🗺️ Map View", command=self.show_map).pack(side='left', padx=5)
        ttk.Button(toolbar, text="📊 Stats", command=self.show_stats).pack(side='left', padx=5)

        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Query frame
        query_frame = ttk.LabelFrame(main_frame, text="Spatial Query")
        query_frame.pack(fill='x', pady=5)

        ttk.Label(query_frame, text="Lat:").grid(row=0, column=0, padx=5)
        self.lat_var = tk.StringVar(value="40.7128")
        ttk.Entry(query_frame, textvariable=self.lat_var, width=12).grid(row=0, column=1)

        ttk.Label(query_frame, text="Lon:").grid(row=0, column=2, padx=5)
        self.lon_var = tk.StringVar(value="-74.0060")
        ttk.Entry(query_frame, textvariable=self.lon_var, width=12).grid(row=0, column=3)

        ttk.Label(query_frame, text="Radius (km):").grid(row=0, column=4, padx=5)
        self.radius_var = tk.StringVar(value="1.0")
        ttk.Entry(query_frame, textvariable=self.radius_var, width=8).grid(row=0, column=5)

        ttk.Button(query_frame, text="Query", command=self.quick_query).grid(row=0, column=6, padx=5)

        # Device selection
        device_frame = ttk.LabelFrame(main_frame, text="Device Selection")
        device_frame.pack(fill='x', pady=5)

        ttk.Label(device_frame, text="Device ID:").grid(row=0, column=0, padx=5)
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(device_frame, textvariable=self.device_var, width=20)
        self.device_combo.grid(row=0, column=1, padx=5)
        self.update_device_list()

        # Results
        results_frame = ttk.LabelFrame(main_frame, text="Results")
        results_frame.pack(fill='both', expand=True, pady=5)

        self.results_text = tk.Text(results_frame, height=15, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(results_frame, command=self.results_text.yview)
        self.results_text.config(yscrollcommand=scrollbar.set)

        self.results_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def load_db(self):
        file_path = filedialog.askopenfilename(
            title="Select FH3 Database",
            filetypes=[("SQLite files", "*.db"), ("All files", "*.*")]
        )
        if file_path:
            self.db_path.set(file_path)
            self.indexer = ForensicH3Analyzer(file_path)
            self.update_device_list()
            messagebox.showinfo("Success", f"Loaded database: {file_path}")

    def init_db(self):
        file_path = filedialog.asksaveasfilename(
            title="Create New FH3 Database",
            defaultextension=".db",
            filetypes=[("SQLite files", "*.db"), ("All files", "*.*")]
        )
        if file_path:
            self.db_path.set(file_path)
            self.indexer = ForensicH3Analyzer(file_path)
            self.update_device_list()
            messagebox.showinfo("Success", f"Created database: {file_path}")

    def update_device_list(self):
        if self.indexer:
            try:
                df = pd.read_sql("SELECT DISTINCT device_id FROM locations", self.indexer.conn)
                devices = df['device_id'].tolist()
                self.device_combo['values'] = devices
                if devices:
                    self.device_var.set(devices[0])
            except:
                self.device_combo['values'] = []

    def add_files(self):
        if not self.indexer:
            messagebox.showerror("Error", "Please load or create a database first")
            return

        files = filedialog.askopenfilenames(
            title="Select Evidence Files",
            filetypes=[("Plist files", "*.plist"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if files:
            case_id = tk.simpledialog.askstring("Case ID", "Enter case ID:")
            if case_id:
                for f in files:
                    self.indexer.add_with_hash(f, case_id)
                self.update_device_list()
                messagebox.showinfo("Success", f"Added {len(files)} files")

    def quick_query(self):
        if not self.indexer:
            messagebox.showerror("Error", "Please load a database first")
            return

        try:
            lat = float(self.lat_var.get())
            lon = float(self.lon_var.get())
            radius = float(self.radius_var.get())

            results = self.indexer.query_hex_neighbors(lat, lon, radius)
            self.display_results(results, f"Locations within {radius}km of ({lat}, {lon})")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid coordinates: {e}")

    def show_map(self):
        if not self.indexer:
            messagebox.showerror("Error", "Please load a database first")
            return

        device_id = self.device_var.get() if self.device_var.get() else None
        output_file = tempfile.mktemp(suffix='.html')
        self.indexer.create_interactive_map(device_id, output_file)
        webbrowser.open(f'file://{output_file}')

    def show_hotspots(self):
        if not self.indexer:
            messagebox.showerror("Error", "Please load a database first")
            return

        device_id = self.device_var.get() if self.device_var.get() else None
        hotspots = self.indexer.hotspot_analysis(device_id)

        result_text = f"Top hotspots for {device_id or 'all devices'}:\n\n"
        for i, (h3_hex, count) in enumerate(list(hotspots.items())[:20]):
            lat, lon = self.indexer.h3_to_geo(h3_hex)
            result_text += f"{i+1}. {h3_hex}: {count} visits\n   Location: {lat:.4f}, {lon:.4f}\n"

        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, result_text)

    def show_anomalies(self):
        if not self.indexer:
            messagebox.showerror("Error", "Please load a database first")
            return

        device_id = self.device_var.get()
        if not device_id:
            messagebox.showerror("Error", "Please select a device")
            return

        anomalies = self.indexer.detect_anomalies(device_id)
        self.display_results(anomalies, f"Anomalies for {device_id}")

    def show_patterns(self):
        if not self.indexer:
            messagebox.showerror("Error", "Please load a database first")
            return

        device_id = self.device_var.get()
        if not device_id:
            messagebox.showerror("Error", "Please select a device")
            return

        patterns = self.indexer.analyze_movement_patterns(device_id)

        result_text = f"Movement patterns for {device_id}:\n\n"
        for key, value in patterns.items():
            result_text += f"{key}: {value}\n"

        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, result_text)

    def show_privacy(self):
        if not self.indexer:
            messagebox.showerror("Error", "Please load a database first")
            return

        device_id = self.device_var.get()
        if not device_id:
            messagebox.showerror("Error", "Please select a device")
            return

        risks = self.indexer.privacy_risk_assessment(device_id)

        result_text = f"Privacy risk assessment for {device_id}:\n\n"
        for key, value in risks.items():
            result_text += f"{key}: {value}\n"

        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, result_text)

    def reverse_geocode(self):
        if not self.indexer:
            messagebox.showerror("Error", "Please load a database first")
            return

        try:
            lat = float(self.lat_var.get())
            lon = float(self.lon_var.get())

            result = self.indexer.reverse_geocode(lat, lon)
            messagebox.showinfo("Reverse Geocode", f"Address: {result['address']}")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid coordinates: {e}")

    def geocode_address(self):
        if not self.indexer:
            messagebox.showerror("Error", "Please load a database first")
            return

        address = tk.simpledialog.askstring("Geocode", "Enter address:")
        if address:
            lat, lon = self.indexer.geocode_address(address)
            if lat and lon:
                self.lat_var.set(str(lat))
                self.lon_var.set(str(lon))
                messagebox.showinfo("Geocode", f"Coordinates: {lat}, {lon}")
            else:
                messagebox.showerror("Error", "Geocoding failed")

    def poi_search(self):
        if not self.indexer:
            messagebox.showerror("Error", "Please load a database first")
            return

        try:
            lat = float(self.lat_var.get())
            lon = float(self.lon_var.get())
            radius = int(tk.simpledialog.askstring("POI Search", "Enter radius (meters):") or "1000")
            poi_type = tk.simpledialog.askstring("POI Search", "Enter POI type (amenity, shop, etc.):") or "amenity"

            pois = self.indexer.search_poi_nearby(lat, lon, radius, poi_type)

            result_text = f"Found {len(pois)} POIs within {radius}m:\n\n"
            for poi in pois[:20]:
                result_text += f"- {poi['name']} ({poi['lat']:.4f}, {poi['lon']:.4f})\n"

            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, result_text)
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def create_map(self):
        if not self.indexer:
            messagebox.showerror("Error", "Please load a database first")
            return

        device_id = self.device_var.get() if self.device_var.get() else None
        output_file = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        if output_file:
            self.indexer.create_interactive_map(device_id, output_file)
            messagebox.showinfo("Success", f"Map saved to {output_file}")

    def export_kml(self):
        if not self.indexer:
            messagebox.showerror("Error", "Please load a database first")
            return

        device_id = self.device_var.get() if self.device_var.get() else None
        output_file = filedialog.asksaveasfilename(
            defaultextension=".kml",
            filetypes=[("KML files", "*.kml"), ("All files", "*.*")]
        )
        if output_file:
            self.indexer.export_kml(device_id, output_file)
            messagebox.showinfo("Success", f"KML exported to {output_file}")

    def export_csv(self):
        if not self.indexer:
            messagebox.showerror("Error", "Please load a database first")
            return

        output_file = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if output_file:
            df = pd.read_sql("SELECT * FROM locations", self.indexer.conn)
            df.to_csv(output_file, index=False)
            messagebox.showinfo("Success", f"CSV exported to {output_file}")

    def show_stats(self):
        if not self.indexer:
            messagebox.showerror("Error", "Please load a database first")
            return

        stats = self.indexer.get_statistics()

        result_text = "Database Statistics:\n\n"
        for key, value in stats.items():
            result_text += f"{key}: {value}\n"

        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, result_text)

    def display_results(self, df, title):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"{title}\n\n")
        if not df.empty:
            self.results_text.insert(tk.END, df.to_string(index=False))
        else:
            self.results_text.insert(tk.END, "No results found")

def main():
    app = FH3GUI()
    app.root.mainloop()

if __name__ == '__main__':
    main()
    
    def show_hotspots(self):
        # Similar to map but with heatmap
        pass  # Implementation similar to show_map with folium.HeatMap
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FH3GUI()
    app.run()