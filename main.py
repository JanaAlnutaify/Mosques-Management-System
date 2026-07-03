
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import difflib
import webbrowser
import tempfile
import os

# try folium for nicer map
try:
    import folium
    FOLIUM_AVAILABLE = True
except Exception:
    FOLIUM_AVAILABLE = False


# Mosque Data Class

class Mosque:
    def __init__(self, id_, name, mtype, address, coordinates, imam_name):
        self.id = id_
        self.name = name
        self.type = mtype
        self.address = address
        self.coordinates = coordinates
        self.imam_name = imam_name


 # Database Class
# Required: init, Display, Search, Insert, Delete, del

class MosqueDB:
    def __init__(self, db_name="mosques_project3.db"):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Mosq (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                address TEXT,
                coordinates TEXT,
                imam_name TEXT
            )
        """)
        self.conn.commit()

    def Display(self):
        self.cur.execute("SELECT id, name, type, address, coordinates, imam_name FROM Mosq")
        return self.cur.fetchall()

    def Search(self, name):
        like = f"%{name}%"
        self.cur.execute("SELECT * FROM Mosq WHERE name LIKE ?", (like,))
        return self.cur.fetchall()

    def Insert(self, id_, name, mtype, address, coordinates, imam_name):
        self.cur.execute(
            "INSERT INTO Mosq (id, name, type, address, coordinates, imam_name) VALUES (?, ?, ?, ?, ?, ?)",
            (id_, name, mtype, address, coordinates, imam_name)
        )
        self.conn.commit()

    def Delete(self, id_):
        self.cur.execute("DELETE FROM Mosq WHERE id = ?", (id_,))
        self.conn.commit()
        return self.cur.rowcount

    def UpdateImam(self, id_, new_imam):
        self.cur.execute("UPDATE Mosq SET imam_name = ? WHERE id = ?", (new_imam, id_))
        self.conn.commit()
        return self.cur.rowcount

    def GetAllNames(self):
        self.cur.execute("SELECT name FROM Mosq")
        return [x[0] for x in self.cur.fetchall()]

    def __del__(self):
        try:
            self.conn.close()
        except:
            pass


 # GUI
class MosquesApp:
    def __init__(self, root):
        self.root = root
        root.title("Mosques Management System")
        root.geometry("1000x380")
        root.resizable(False, False)

        # Colors
        self.outer_yellow = "#e6c975"
        self.inner_gray = "#efefef"
        self.button_gray = "#d7d7d7"

        # Database
        self.db = MosqueDB()

        # Variables
        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.type_var = tk.StringVar(value="Masjid")
        self.address_var = tk.StringVar()
        self.coord_var = tk.StringVar()
        self.imam_var = tk.StringVar()

        # Build UI
        self.build_ui()
        self.refresh_listbox()

    #  Interface
    def build_ui(self):

        # Top title
        title_frame = tk.Frame(self.root, bg=self.outer_yellow, height=30)
        title_frame.pack(fill="x", side="top")

        title_label = tk.Label(
            title_frame,
            text="Mosques Management System",
            bg=self.outer_yellow,
            font=("Arial", 12, "bold")
        )
        title_label.place(relx=0.5, rely=0.5, anchor="center")

        # outer
        outer = tk.Frame(self.root, bg=self.outer_yellow, padx=6, pady=6)
        outer.pack(fill="both", expand=True)

        # Inner
        inner = tk.Frame(outer, bg=self.inner_gray)
        inner.pack(fill="both", expand=True)

        # Left
        left = tk.Frame(inner, bg=self.inner_gray)
        left.place(x=10, y=10, width=460, height=300)

        # Right
        right = tk.Frame(inner, bg=self.inner_gray)
        right.place(x=490, y=10, width=480, height=300)

         #   INPUT FIELDS
        tk.Label(left, text="ID", bg=self.inner_gray).place(x=6, y=6)
        tk.Entry(left, textvariable=self.id_var, width=12).place(x=60, y=4)

        tk.Label(left, text="Name", bg=self.inner_gray).place(x=200, y=6)
        tk.Entry(left, textvariable=self.name_var, width=28).place(x=250, y=4)

        tk.Label(left, text="Type", bg=self.inner_gray).place(x=6, y=36)

         #  COMBOBOX
        self.type_box = ttk.Combobox(


            left,
            textvariable=self.type_var,
            values=["Masjid", "Small Prayer Area", "Large Mosque"],
            state="readonly",
            width=20
        )
        self.type_box.place(x=60, y=34)

        tk.Label(left, text="Address", bg=self.inner_gray).place(x=200, y=36)
        tk.Entry(left, textvariable=self.address_var, width=28).place(x=250, y=34)

        tk.Label(left, text="Coordinates", bg=self.inner_gray).place(x=6, y=66)
        tk.Entry(left, textvariable=self.coord_var, width=18).place(x=90, y=64)

        tk.Label(left, text="Imam_name", bg=self.inner_gray).place(x=200, y=66)
        tk.Entry(left, textvariable=self.imam_var, width=20).place(x=280, y=64)

         #BUTTONS
        tk.Button(left, text="Display All", width=14, bg=self.button_gray,
                  command=self.on_display_all).place(x=40, y=110)

        tk.Button(left, text="Search By Name", width=14, bg=self.button_gray,
                  command=self.on_search).place(x=180, y=110)

        tk.Button(left, text="Update Entry", width=14, bg=self.button_gray,
                  command=self.on_update_imam).place(x=320, y=110)

        tk.Button(left, text="Add Entry", width=14, bg=self.button_gray,
                  command=self.on_add).place(x=40, y=150)

        tk.Button(left, text="Delete entry", width=14, bg=self.button_gray,
                  command=self.on_delete).place(x=180, y=150)

        tk.Button(left, text="Display on Map", width=14, bg=self.button_gray,
                  command=self.on_display_map).place(x=320, y=150)

        box = tk.Frame(right, bg="white", bd=1)
        box.place(x=6, y=6, width=448, height=288)
     #LISTBOX
        self.listbox = tk.Listbox(box, width=60, height=16)
        self.listbox.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        self.listbox.bind("<<ListboxSelect>>", self.on_list_select)

        sb = tk.Scrollbar(box, orient="vertical", command=self.listbox.yview)
        sb.pack(side="right", fill="y", padx=(0, 6), pady=6)
        self.listbox.config(yscrollcommand=sb.set)

        self.status = tk.Label(self.root, text="Ready", bg=self.outer_yellow)
        self.status.pack(side="bottom", fill="x")

    # CORE FUNCTIONS
    def refresh_listbox(self, rows=None):
        self.listbox.delete(0, tk.END)
        if rows is None:
            rows = self.db.Display()
        for r in rows:
            text = f"ID:{r[0]} | Name:{r[1]} | Type:{r[2]} | Addr:{r[3]} | Coords:{r[4]} | Imam:{r[5]}"
            self.listbox.insert(tk.END, text)
        self.status.config(text=f"Showing {len(rows)} record(s)")

    def clear_fields(self):
        self.id_var.set("")
        self.name_var.set("")
        self.type_var.set("Masjid")
        self.address_var.set("")
        self.coord_var.set("")
        self.imam_var.set("")

    def on_list_select(self, event):
        sel = event.widget.curselection()
        if not sel:
            return
        idx = sel[0]
        line = self.listbox.get(idx)
        try:
            parts = line.split(" | ")
            self.id_var.set(parts[0].replace("ID:", ""))
            self.name_var.set(parts[1].replace("Name:", ""))
            self.type_var.set(parts[2].replace("Type:", ""))
            self.address_var.set(parts[3].replace("Addr:", ""))
            self.coord_var.set(parts[4].replace("Coords:", ""))
            self.imam_var.set(parts[5].replace("Imam:", ""))
        except:
            pass

    #   Add
    def on_add(self):
        if not self.id_var.get().isdigit():
            messagebox.showerror("Error", "ID must be integer")
            return

        try:
            self.db.Insert(
                int(self.id_var.get()),
                self.name_var.get(),
                self.type_var.get(),
                self.address_var.get(),
                self.coord_var.get(),
                self.imam_var.get()
            )
            messagebox.showinfo("Done", "Entry added.")
            self.refresh_listbox()
            self.clear_fields()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "ID already exists")

    #   Delete
    def on_delete(self):
        if not self.id_var.get().isdigit():
            messagebox.showerror("Error", "Enter ID to delete")
            return

        if messagebox.askyesno("Confirm", "Delete this entry?"):
            rows = self.db.Delete(int(self.id_var.get()))
            if rows:
                messagebox.showinfo("Deleted", "Entry removed.")
                self.refresh_listbox()
                self.clear_fields()

    #   Search
    def on_search(self):
        name = self.name_var.get().strip()

        # If name input is empty → ask user
        if not name:
            name = simpledialog.askstring("Search", "Enter mosque name to search:")
            if not name:
                return

        # First: exact partial search
        rows = self.db.Search(name)

        if rows:
            # Found results → display them
            self.refresh_listbox(rows)
            self.status.config(text=f"Search found {len(rows)} record(s).")
            return

        # If no exact match → check if DB empty
        all_names = self.db.GetAllNames()
        if not all_names:
            messagebox.showinfo("Empty", "Database is empty. Add entries first.")
            return

        # Try suggestions
        suggestions = difflib.get_close_matches(name, all_names, n=5, cutoff=0.5)

        if not suggestions:
            # No match + no suggestions
            messagebox.showerror("Not Found", f"No mosque with name '{name}' was found.")
            return

        # Show suggestions and let user choose
        suggestion_text = "\n".join(suggestions)
        chosen = simpledialog.askstring(
            "Did you mean?",
            f"No exact match found.\n\nClose matches:\n{suggestion_text}\n\nType one of the above to search:"
        )

        if not chosen:
            return

        rows2 = self.db.Search(chosen)
        if rows2:
            self.refresh_listbox(rows2)
            self.status.config(text=f"Found {len(rows2)} record(s) for '{chosen}'.")
        else:
            messagebox.showerror("Not Found", f"No mosque with name '{chosen}' was found.")

    #   Update Imam
    def on_update_imam(self):
        if not self.id_var.get().isdigit():
            messagebox.showerror("Error", "Enter valid ID")
            return

        new = simpledialog.askstring("Update Imam", "Enter new imam name:")
        if not new:
            return

        rows = self.db.UpdateImam(int(self.id_var.get()), new)
        if rows:
            messagebox.showinfo("Updated", "Imam updated.")
            self.refresh_listbox()
            self.clear_fields()

    #  Display All
    def on_display_all(self):
        self.refresh_listbox(self.db.Display())

    #   Display on Map
    def on_display_map(self):
        coords = self.coord_var.get()
        if not coords or "," not in coords:
            messagebox.showerror("Error", "Coordinates must be: lat,lon")
            return

        lat, lon = coords.split(",")
        lat, lon = float(lat), float(lon)

        if FOLIUM_AVAILABLE:
            m = folium.Map(location=[lat, lon], zoom_start=16)
            folium.Marker([lat, lon], popup=self.name_var.get()).add_to(m)

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
            m.save(tmp.name)
            webbrowser.open("file://" + os.path.realpath(tmp.name))
        else:
            webbrowser.open(f"https://www.google.com/maps?q={lat},{lon}")


# RUN APP

if __name__ == "__main__":
    root = tk.Tk()
    app = MosquesApp(root)
    root.mainloop()
