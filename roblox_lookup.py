import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image
try:
    from PIL import ImageTk
    IMAGETK_AVAILABLE = True
except ImportError:
    ImageTk = None
    IMAGETK_AVAILABLE = False
from io import BytesIO
from datetime import datetime
import threading
import re
import webbrowser
from difflib import SequenceMatcher


class RobloxUserInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RBLX Lookup")
        self.root.geometry("1000x900")
        # Dark minimalist theme colors (matching the UI style)
        self.bg_color = "#1a1a1a"  # Very dark grey/black background
        self.section_bg = "#2a2a2a"  # Dark grey for sections/panels
        self.panel_bg = "#252525"  # Slightly lighter for panels
        self.text_color = "#d0d0d0"  # Light grey text
        self.border_color = "#3a3a3a"  # Subtle border color
        self.accent_color = "#4a9eff"  # Blue accent for links/buttons
        self.warning_color = "#d4d400"  # Yellowish-green for warnings
        self.title_color = "#e0e0e0"  # Light grey for titles
        self.label_color = "#b0b0b0"  # Medium grey for labels
        
        
        self.root.configure(bg=self.bg_color)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Title.TLabel', font=('Arial', 18, 'bold'), background=self.bg_color, foreground=self.title_color)
        self.style.configure('Info.TLabel', font=('Arial', 10), background=self.section_bg, foreground=self.text_color)
        self.style.configure('Custom.TButton', font=('Arial', 11, 'bold'))
        
        # Store avatar image reference
        self.avatar_image = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container - matching reference layout
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main content frame with border
        content_border = tk.Frame(main_frame, bg=self.border_color, relief=tk.FLAT, borderwidth=1)
        content_border.pack(fill=tk.BOTH, expand=True)
        
        content_frame = tk.Frame(content_border, bg=self.panel_bg)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Top section: Title and Options
        top_section = tk.Frame(content_frame, bg=self.panel_bg)
        top_section.pack(fill=tk.X, padx=15, pady=15)
        
        # Left side: Title and version
        left_top = tk.Frame(top_section, bg=self.panel_bg)
        left_top.pack(side=tk.LEFT, fill=tk.Y)
        
        # Icon placeholder (can be replaced with actual icon)
        icon_label = tk.Label(
            left_top,
            text="🔍",
            font=('Arial', 24),
            bg=self.panel_bg,
            fg=self.title_color
        )
        icon_label.pack(anchor=tk.W, pady=(0, 5))
        
        title_label = tk.Label(
            left_top,
            text="Roblox Lookup Tool",
            font=('Arial', 16, 'bold'),
            bg=self.panel_bg,
            fg=self.title_color
        )
        title_label.pack(anchor=tk.W, pady=(0, 3))
        
        version_label = tk.Label(
            left_top,
            text="Updated 2024, V1.0",
            font=('Arial', 8),
            bg=self.panel_bg,
            fg=self.label_color
        )
        version_label.pack(anchor=tk.W)
        
        # Right side: Empty for now (can add options later if needed)
        right_top = tk.Frame(top_section, bg=self.panel_bg)
        right_top.pack(side=tk.RIGHT)
        
        # Search section
        search_section = tk.Frame(content_frame, bg=self.panel_bg)
        search_section.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        search_frame = tk.Frame(search_section, bg=self.panel_bg)
        search_frame.pack(fill=tk.X)
        
        # Username entry
        entry_label = tk.Label(
            search_frame,
            text="Username:",
            font=('Arial', 10),
            bg=self.panel_bg,
            fg=self.text_color
        )
        entry_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # Entry field with border
        entry_container = tk.Frame(search_frame, bg=self.panel_bg)
        entry_container.pack(side=tk.LEFT, padx=(0, 8))
        
        self.username_entry = tk.Entry(
            entry_container,
            font=('Arial', 10),
            width=22,
            bg=self.section_bg,
            fg=self.text_color,
            insertbackground=self.text_color,
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.border_color,
            highlightcolor=self.accent_color
        )
        self.username_entry.pack(padx=2, pady=2)
        self.username_entry.bind('<Return>', lambda e: self.fetch_user_info())
        
        # Search button with minimalist style
        self.search_button = self._create_minimalist_button(search_frame, "Search", width=12, command=self.fetch_user_info)
        self.search_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # Checkbox for alt account detection
        self.check_alt_accounts = tk.BooleanVar(value=False)
        alt_checkbox = tk.Checkbutton(
            search_frame,
            text="Check for alt accounts",
            font=('Arial', 9),
            bg=self.panel_bg,
            fg=self.text_color,
            activebackground=self.panel_bg,
            activeforeground=self.text_color,
            selectcolor=self.section_bg,
            variable=self.check_alt_accounts
        )
        alt_checkbox.pack(side=tk.LEFT)
        
        # Main content area - split layout
        main_content = tk.Frame(content_frame, bg=self.panel_bg)
        main_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Create scrollable canvas for content
        canvas_frame = tk.Frame(main_content, bg=self.panel_bg)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg=self.panel_bg, highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.panel_bg)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Content container
        self.content_frame = scrollable_frame
        
        # Status panel at bottom (matching reference UI)
        status_panel = tk.Frame(content_frame, bg=self.panel_bg)
        status_panel.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        status_label = tk.Label(
            status_panel,
            text="Status",
            font=('Arial', 10, 'bold'),
            bg=self.panel_bg,
            fg=self.title_color
        )
        status_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Status text area with border
        status_border = tk.Frame(status_panel, bg=self.border_color, relief=tk.FLAT, borderwidth=1)
        status_border.pack(fill=tk.BOTH, expand=True)
        
        status_inner = tk.Frame(status_border, bg=self.section_bg)
        status_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Status text widget for multiple lines
        self.status_text = tk.Text(
            status_inner,
            font=('Arial', 9),
            bg=self.section_bg,
            fg=self.text_color,
            relief=tk.FLAT,
            borderwidth=0,
            wrap=tk.WORD,
            height=5,
            padx=10,
            pady=8
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)
        self.status_text.insert('1.0', "Welcome back,\n")
        self.status_text.config(state=tk.DISABLED)
        
        # Keep loading_label reference for compatibility
        class StatusLabel:
            def __init__(self, status_text):
                self.status_text = status_text
            def config(self, **kwargs):
                if 'text' in kwargs:
                    self.status_text.config(state=tk.NORMAL)
                    self.status_text.delete('1.0', tk.END)
                    self.status_text.insert('1.0', kwargs['text'])
                    self.status_text.config(state=tk.DISABLED)
        
        self.loading_label = StatusLabel(self.status_text)
        
        # Initialize info widgets (will be populated when data is loaded)
        self.info_widgets = {}
        self._create_info_widgets()
    
    def _create_minimalist_button(self, parent, text, width=10, command=None):
        """Create a minimalist button matching the UI style"""
        button = tk.Button(
            parent,
            text=text,
            font=('Arial', 9),
            bg=self.section_bg,
            fg=self.text_color,
            activebackground=self.panel_bg,
            activeforeground=self.text_color,
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.border_color,
            width=width,
            cursor="hand2",
            command=command
        )
        return button
    
    def _update_status(self, message, is_warning=False):
        """Update status panel with message"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete('1.0', tk.END)
        if is_warning:
            self.status_text.insert('1.0', message, 'warning')
            self.status_text.tag_config('warning', foreground=self.warning_color)
        else:
            self.status_text.insert('1.0', message)
        self.status_text.config(state=tk.DISABLED)
        
    def _create_info_widgets(self):
        """Create all info display widgets"""
        # Top section: Avatar and basic info
        top_section = tk.Frame(self.content_frame, bg=self.bg_color)
        top_section.pack(fill=tk.X, pady=(0, 20))
        
        # Avatar frame with border
        avatar_outer = tk.Frame(top_section, bg=self.border_color, relief=tk.FLAT, borderwidth=1)
        avatar_outer.pack(side=tk.LEFT, padx=(0, 10))
        avatar_container = tk.Frame(avatar_outer, bg=self.section_bg)
        avatar_container.pack(padx=1, pady=1)
        
        self.avatar_label = tk.Label(
            avatar_container,
            text="Avatar",
            font=('Arial', 9),
            bg=self.section_bg,
            fg=self.text_color,
            width=18,
            height=8
        )
        self.avatar_label.pack(padx=8, pady=8)
        
        # Basic info frame with border
        basic_outer = tk.Frame(top_section, bg=self.border_color, relief=tk.FLAT, borderwidth=1)
        basic_outer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        basic_info_frame = tk.Frame(basic_outer, bg=self.section_bg)
        basic_info_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        basic_title = tk.Label(
            basic_info_frame,
            text="Basic Information",
            font=('Arial', 10, 'bold'),
            bg=self.section_bg,
            fg=self.title_color
        )
        basic_title.pack(anchor=tk.W, padx=10, pady=(10, 6))
        
        self.info_widgets['username'] = self._create_info_row(basic_info_frame, "Username:", "")
        self.info_widgets['display_name'] = self._create_info_row(basic_info_frame, "Display Name:", "")
        self.info_widgets['user_id'] = self._create_info_row(basic_info_frame, "User ID:", "")
        self.info_widgets['description'] = self._create_info_row(basic_info_frame, "Description:", "", multiline=True)
        
        # Account details section
        account_section = self._create_section("📅 Account Details")
        self.info_widgets['created'] = self._create_info_row(account_section, "Created:", "")
        self.info_widgets['is_banned'] = self._create_info_row(account_section, "Is Banned:", "")
        self.info_widgets['verified'] = self._create_info_row(account_section, "Verified Badge:", "")
        
        # Social statistics section
        social_section = self._create_section("👥 Social Statistics")
        self.info_widgets['friends'] = self._create_info_row(social_section, "Friends:", "")
        self.info_widgets['followers'] = self._create_info_row(social_section, "Followers:", "")
        self.info_widgets['following'] = self._create_info_row(social_section, "Following:", "")
        
        # Achievements section
        achievements_section = self._create_section("🏆 Achievements")
        self.info_widgets['badges'] = self._create_info_row(achievements_section, "Badges:", "")
        self.info_widgets['groups'] = self._create_info_row(achievements_section, "Groups:", "")
        
        # Presence section
        presence_section = self._create_section("🌐 Status")
        self.info_widgets['status'] = self._create_info_row(presence_section, "Status:", "")
        self.info_widgets['current_game'] = self._create_info_row(presence_section, "Current Game:", "")
        self.info_widgets['last_location'] = self._create_info_row(presence_section, "Last Location:", "")
        
        # Owned Groups section
        owned_groups_section = self._create_section("👑 Owned Groups")
        self.info_widgets['owned_groups'] = self._create_info_row(owned_groups_section, "Groups:", "", multiline=True)
        
        # Owned Games section
        owned_games_section = self._create_section("🎮 Owned Games")
        self.info_widgets['owned_games'] = self._create_info_row(owned_games_section, "Games:", "", multiline=True)
        
        # Possible Alt Accounts section
        alt_accounts_section = self._create_section("🔍 Possible Alt Accounts")
        self.info_widgets['alt_accounts'] = self._create_info_row(alt_accounts_section, "Potential Alts:", "", multiline=True)
        
        # Server Search section
        server_search_section = self._create_section("🎮 Snipe Server")
        server_search_frame = tk.Frame(server_search_section, bg=self.section_bg)
        server_search_frame.pack(fill=tk.X, padx=15, pady=10)
        
        game_id_label = tk.Label(
            server_search_frame,
            text="Game ID (Universe ID):",
            font=('Arial', 10, 'bold'),
            bg=self.section_bg,
            fg=self.label_color
        )
        game_id_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Entry with border
        entry_wrapper = tk.Frame(server_search_frame, bg=self.bg_color)
        entry_wrapper.pack(side=tk.LEFT, padx=(0, 8))
        self.game_id_entry = tk.Entry(
            entry_wrapper,
            font=('Arial', 9),
            width=18,
            bg=self.panel_bg,
            fg=self.text_color,
            insertbackground=self.text_color,
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.border_color,
            highlightcolor=self.accent_color
        )
        self.game_id_entry.pack(padx=2, pady=2)
        
        # Buttons with minimalist style
        self.search_servers_button = tk.Button(
            server_search_frame,
            text="Search Servers",
            font=('Arial', 9),
            bg=self.panel_bg,
            fg=self.text_color,
            activebackground=self.section_bg,
            activeforeground=self.text_color,
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.border_color,
            padx=12,
            pady=3,
            cursor="hand2",
            command=self.search_user_in_servers
        )
        self.search_servers_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Button to use current game ID
        use_current_button = tk.Button(
            server_search_frame,
            text="Use Current Game",
            font=('Arial', 8),
            bg=self.panel_bg,
            fg=self.text_color,
            activebackground=self.section_bg,
            activeforeground=self.text_color,
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.border_color,
            padx=8,
            pady=3,
            cursor="hand2",
            command=self.use_current_game_id
        )
        use_current_button.pack(side=tk.LEFT)
        
        self.info_widgets['server_search_result'] = self._create_info_row(server_search_section, "Result:", "", multiline=True)
        
        # Add info label about API limitations - warning style
        info_label = tk.Label(
            server_search_section,
            text="⚠ Note: Roblox API doesn't provide player lists. If user is in game, all servers will be shown.",
            font=('Arial', 7),
            bg=self.panel_bg,
            fg=self.warning_color,
            wraplength=800
        )
        info_label.pack(anchor=tk.W, padx=12, pady=(0, 8))
        
        # Links section
        links_section = self._create_section("🔗 Links")
        self.info_widgets['profile_link'] = self._create_info_row(links_section, "Profile:", "", link=True)
        self.info_widgets['avatar_link'] = self._create_info_row(links_section, "Avatar:", "", link=True)
        
    def _create_section(self, title):
        """Create a section with title"""
        section_frame = tk.Frame(self.content_frame, bg=self.section_bg, relief=tk.RAISED, borderwidth=2)
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(
            section_frame,
            text=title,
            font=('Arial', 14, 'bold'),
            bg=self.section_bg,
            fg=self.title_color
        )
        title_label.pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        return section_frame
    
    def _create_info_row(self, parent, label_text, value_text, multiline=False, link=False):
        """Create an info row with label and value - minimalist style"""
        row_frame = tk.Frame(parent, bg=self.panel_bg)
        row_frame.pack(fill=tk.X, padx=12, pady=4)
        
        label = tk.Label(
            row_frame,
            text=label_text,
            font=('Arial', 9),
            bg=self.panel_bg,
            fg=self.label_color,
            width=15,
            anchor=tk.W
        )
        label.pack(side=tk.LEFT, padx=(0, 10))
        
        if link:
            value_label = tk.Label(
                row_frame,
                text=value_text,
                font=('Arial', 9),
                bg=self.panel_bg,
                fg=self.accent_color,
                cursor="hand2",
                anchor=tk.W
            )
            value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            return {'label': label, 'value': value_label, 'type': 'link'}
        elif multiline:
            value_label = tk.Label(
                row_frame,
                text=value_text,
                font=('Arial', 8),
                bg=self.panel_bg,
                fg=self.text_color,
                anchor=tk.W,
                justify=tk.LEFT,
                wraplength=700
            )
            value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            return {'label': label, 'value': value_label, 'type': 'multiline'}
        else:
            value_label = tk.Label(
                row_frame,
                text=value_text,
                font=('Arial', 9),
                bg=self.panel_bg,
                fg=self.text_color,
                anchor=tk.W
            )
            value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            return {'label': label, 'value': value_label, 'type': 'normal'}
    
    def fetch_user_info(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showwarning("Warning", "Please enter a username")
            return
        
        # Clear previous data
        self._clear_info_widgets()
        
        # Disable button and show loading
        self.search_button.config(state=tk.DISABLED)
        self._update_status("Loading user information...")
        self.avatar_label.config(image='', text="Loading avatar...")
        self.root.update()
        
        # Fetch in a separate thread to avoid freezing UI
        thread = threading.Thread(target=self._fetch_user_info_thread, args=(username,))
        thread.daemon = True
        thread.start()
        
    def _clear_info_widgets(self):
        """Clear all info widgets"""
        for widget_info in self.info_widgets.values():
            if widget_info['type'] == 'link':
                widget_info['value'].config(text="", cursor="")
            else:
                widget_info['value'].config(text="")
    
    def _fetch_user_info_thread(self, username):
        try:
            # Step 1: Get user ID from username
            user_id = self.get_user_id(username)
            if not user_id:
                self.root.after(0, self._show_error, f"User '{username}' not found")
                return
            
            # Step 2: Get user information
            user_info = self.get_user_info(user_id)
            if not user_info:
                self.root.after(0, self._show_error, "Failed to fetch user information")
                return
            
            # Step 3: Get additional user data
            additional_info = self.get_additional_user_info(user_id)
            
            # Step 4: Get owned groups
            owned_groups = self.get_owned_groups(user_id)
            additional_info['owned_groups'] = owned_groups
            
            # Step 5: Get owned games
            owned_games = self.get_owned_games(user_id)
            additional_info['owned_games'] = owned_games
            
            # Step 6: Get possible alt accounts (only if checkbox is checked)
            if self.check_alt_accounts.get():
                self.root.after(0, lambda: self._update_status("Analyzing friends for alt accounts..."))
                alt_accounts = self.detect_alt_accounts(user_id, user_info)
                additional_info['alt_accounts'] = alt_accounts
            else:
                additional_info['alt_accounts'] = []
            
            # Step 7: Get avatar
            avatar_url = self.get_avatar_url(user_id)
            
            # Update UI in main thread
            self.root.after(0, self._update_ui, user_info, additional_info, avatar_url, username)
            
        except Exception as e:
            self.root.after(0, self._show_error, f"Error: {str(e)}")
    
    def get_user_id(self, username):
        """Get user ID from username"""
        try:
            url = "https://users.roblox.com/v1/usernames/users"
            payload = {
                "usernames": [username],
                "excludeBannedUsers": False
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("data") and len(data["data"]) > 0:
                return data["data"][0]["id"]
            return None
        except Exception as e:
            print(f"Error getting user ID: {e}")
            return None
    
    def get_user_info(self, user_id):
        """Get basic user information"""
        try:
            url = f"https://users.roblox.com/v1/users/{user_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    def get_additional_user_info(self, user_id):
        """Get additional user information like friends count, badges, etc."""
        additional_info = {}
        
        try:
            # Get friends count
            url = f"https://friends.roblox.com/v1/users/{user_id}/friends/count"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                additional_info['friends_count'] = response.json().get('count', 0)
        except:
            additional_info['friends_count'] = "N/A"
        
        try:
            # Get followers count
            url = f"https://friends.roblox.com/v1/users/{user_id}/followers/count"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                additional_info['followers_count'] = response.json().get('count', 0)
        except:
            additional_info['followers_count'] = "N/A"
        
        try:
            # Get following count
            url = f"https://friends.roblox.com/v1/users/{user_id}/followings/count"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                additional_info['following_count'] = response.json().get('count', 0)
        except:
            additional_info['following_count'] = "N/A"
        
        try:
            # Get badges count
            url = f"https://badges.roblox.com/v1/users/{user_id}/badges/count"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                additional_info['badges_count'] = response.json().get('count', 0)
        except:
            additional_info['badges_count'] = "N/A"
        
        try:
            # Get groups count
            url = f"https://groups.roblox.com/v1/users/{user_id}/groups/roles"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                additional_info['groups_count'] = len(response.json().get('data', []))
        except:
            additional_info['groups_count'] = "N/A"
        
        try:
            # Get user presence
            url = f"https://presence.roblox.com/v1/presence/users"
            payload = {"userIds": [user_id]}
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                presence_data = response.json().get('userPresences', [])
                if presence_data:
                    presence = presence_data[0]
                    additional_info['presence'] = presence.get('userPresenceType', 'Unknown')
                    additional_info['last_location'] = presence.get('lastLocation', 'Unknown')
                    
                    # Get current game if user is playing
                    current_game = "N/A"
                    if presence.get('userPresenceType') == 'InGame' or presence.get('userPresenceType') == 'InStudio':
                        universe_id = presence.get('universeId')
                        place_id = presence.get('placeId')
                        if universe_id:
                            # Get game name from universe ID
                            game_name = self.get_game_name(universe_id)
                            if game_name:
                                current_game = f"{game_name} (Universe: {universe_id})"
                            else:
                                current_game = f"Universe: {universe_id}"
                        elif place_id:
                            current_game = f"Place: {place_id}"
                    additional_info['current_game'] = current_game
                else:
                    additional_info['presence'] = "N/A"
                    additional_info['last_location'] = "N/A"
                    additional_info['current_game'] = "N/A"
            else:
                additional_info['presence'] = "N/A"
                additional_info['last_location'] = "N/A"
                additional_info['current_game'] = "N/A"
        except Exception as e:
            print(f"Error getting presence: {e}")
            additional_info['presence'] = "N/A"
            additional_info['last_location'] = "N/A"
            additional_info['current_game'] = "N/A"
        
        return additional_info
    
    def get_game_name(self, universe_id):
        """Get game name from universe ID"""
        try:
            url = f"https://games.roblox.com/v1/games?universeIds={universe_id}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json().get('data', [])
                if data:
                    return data[0].get('name', None)
        except Exception as e:
            print(f"Error getting game name: {e}")
        return None
    
    def get_owned_groups(self, user_id):
        """Get groups owned by the user"""
        owned_groups = []
        try:
            url = f"https://groups.roblox.com/v1/users/{user_id}/groups/roles"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json().get('data', [])
                for group_role in data:
                    if group_role.get('role', {}).get('rank') == 255:  # Owner rank
                        group = group_role.get('group', {})
                        owned_groups.append({
                            'id': group.get('id'),
                            'name': group.get('name'),
                            'member_count': group.get('memberCount', 0)
                        })
        except Exception as e:
            print(f"Error getting owned groups: {e}")
        return owned_groups
    
    def get_owned_games(self, user_id):
        """Get games/experiences created by the user"""
        owned_games = []
        try:
            url = f"https://games.roblox.com/v2/users/{user_id}/games?accessFilter=2&limit=50&sortOrder=Asc"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json().get('data', [])
                for game in data:
                    owned_games.append({
                        'id': game.get('id'),
                        'name': game.get('name'),
                        'playing': game.get('playing', 0),
                        'visits': game.get('visits', 0),
                        'created': game.get('created', '')
                    })
        except Exception as e:
            print(f"Error getting owned games: {e}")
        return owned_games
    
    def detect_alt_accounts(self, user_id, user_info):
        """Detect possible alt accounts by analyzing friends"""
        potential_alts = []
        try:
            # Get user's creation date
            user_created = user_info.get('created', '')
            user_username = user_info.get('name', '').lower()
            user_description = user_info.get('description', '').lower()
            
            # Get friends list (limited to first 100 for performance)
            url = f"https://friends.roblox.com/v1/users/{user_id}/friends?userSort=0&limit=100"
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                return potential_alts
            
            friends = response.json().get('data', [])
            if not friends:
                return potential_alts
            
            # Analyze each friend for alt account indicators
            for friend in friends[:50]:  # Limit to 50 for performance
                friend_id = friend.get('id')
                friend_name = friend.get('name', '').lower()
                
                # Get friend's info
                try:
                    friend_info = self.get_user_info(friend_id)
                    if not friend_info:
                        continue
                    
                    friend_created = friend_info.get('created', '')
                    friend_description = friend_info.get('description', '').lower()
                    friend_friends_count = self._get_friends_count(friend_id)
                    
                    score = 0
                    reasons = []
                    
                    # Check 1: Similar creation date (within 30 days)
                    if user_created and friend_created:
                        try:
                            user_date = datetime.fromisoformat(user_created.replace('Z', '+00:00'))
                            friend_date = datetime.fromisoformat(friend_created.replace('Z', '+00:00'))
                            days_diff = abs((user_date - friend_date).days)
                            if days_diff <= 30:
                                score += 3
                                reasons.append(f"Created {days_diff} days apart")
                        except:
                            pass
                    
                    # Check 2: Similar username patterns
                    similarity = SequenceMatcher(None, user_username, friend_name).ratio()
                    if similarity > 0.6:
                        score += 2
                        reasons.append(f"Similar username ({similarity:.0%} match)")
                    
                    # Check 3: Common username patterns (numbers, underscores, etc.)
                    user_base = re.sub(r'[0-9_\-]', '', user_username)
                    friend_base = re.sub(r'[0-9_\-]', '', friend_name)
                    if user_base and friend_base and user_base == friend_base:
                        score += 3
                        reasons.append("Same base username with variations")
                    
                    # Check 4: Similar descriptions
                    if user_description and friend_description:
                        desc_similarity = SequenceMatcher(None, user_description[:50], friend_description[:50]).ratio()
                        if desc_similarity > 0.7:
                            score += 2
                            reasons.append("Similar description")
                    
                    # Check 5: Low friend count (alts often have few friends)
                    if friend_friends_count < 10:
                        score += 1
                        reasons.append(f"Low friend count ({friend_friends_count})")
                    
                    # Check 6: Both have similar low activity (few badges, groups)
                    friend_badges = self._get_badges_count(friend_id)
                    if friend_badges < 5:
                        score += 1
                        reasons.append(f"Low badge count ({friend_badges})")
                    
                    # If score is high enough, consider it a potential alt
                    if score >= 4:
                        potential_alts.append({
                            'username': friend.get('name'),
                            'id': friend_id,
                            'score': score,
                            'reasons': reasons
                        })
                
                except Exception as e:
                    continue
            
            # Sort by score (highest first)
            potential_alts.sort(key=lambda x: x['score'], reverse=True)
            
        except Exception as e:
            print(f"Error detecting alt accounts: {e}")
        
        return potential_alts[:10]  # Return top 10
    
    def _get_friends_count(self, user_id):
        """Helper to get friends count"""
        try:
            url = f"https://friends.roblox.com/v1/users/{user_id}/friends/count"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json().get('count', 0)
        except:
            pass
        return 0
    
    def _get_badges_count(self, user_id):
        """Helper to get badges count"""
        try:
            url = f"https://badges.roblox.com/v1/users/{user_id}/badges/count"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json().get('count', 0)
        except:
            pass
        return 0
    
    def get_avatar_url(self, user_id):
        """Get user avatar URL using current Roblox API"""
        try:
            # Updated endpoint: /v1/users/avatar instead of /v1/users/avatar-headshot
            url = f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=150x150&format=Png&isCircular=false"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("data") and len(data["data"]) > 0:
                return data["data"][0]["imageUrl"]
        except Exception as e:
            print(f"Error getting avatar: {e}")
        return None
    
    def _update_ui(self, user_info, additional_info, avatar_url, username):
        """Update UI with fetched information"""
        try:
            # Display avatar - fixed to work properly
            if avatar_url:
                try:
                    # Always try to load and display the image
                    response = requests.get(avatar_url, timeout=10)
                    response.raise_for_status()
                    img = Image.open(BytesIO(response.content))
                    img = img.resize((150, 150), Image.Resampling.LANCZOS)
                    
                    # Convert to PhotoImage and display
                    if IMAGETK_AVAILABLE and ImageTk is not None:
                        photo = ImageTk.PhotoImage(img)
                        # Clear any existing text
                        self.avatar_label.config(image=photo, text="")
                        # Keep reference to prevent garbage collection - this is critical!
                        self.avatar_image = photo
                        self.avatar_label.image = photo
                    else:
                        # ImageTk not available
                        self.avatar_label.config(image='', text="ImageTk not\navailable")
                except requests.RequestException as e:
                    error_msg = str(e)[:40]
                    self.avatar_label.config(image='', text=f"Network error:\n{error_msg}")
                    print(f"Avatar fetch error: {e}")
                except Exception as e:
                    error_msg = str(e)[:40]
                    self.avatar_label.config(image='', text=f"Error:\n{error_msg}")
                    print(f"Avatar display error: {e}")
            else:
                self.avatar_label.config(image='', text="No avatar URL\navailable")
            
            # Update basic information
            self.info_widgets['username']['value'].config(text=user_info.get('name', 'N/A'))
            self.info_widgets['display_name']['value'].config(text=user_info.get('displayName', 'N/A'))
            self.info_widgets['user_id']['value'].config(text=str(user_info.get('id', 'N/A')))
            desc = user_info.get('description', 'No description')
            if not desc:
                desc = "No description"
            self.info_widgets['description']['value'].config(text=desc)
            
            # Update account details
            self.info_widgets['created']['value'].config(text=self.format_date(user_info.get('created')))
            self.info_widgets['is_banned']['value'].config(text="Yes" if user_info.get('isBanned', False) else "No")
            self.info_widgets['verified']['value'].config(text="Yes" if user_info.get('hasVerifiedBadge', False) else "No")
            
            # Update social statistics
            self.info_widgets['friends']['value'].config(text=str(additional_info.get('friends_count', 'N/A')))
            self.info_widgets['followers']['value'].config(text=str(additional_info.get('followers_count', 'N/A')))
            self.info_widgets['following']['value'].config(text=str(additional_info.get('following_count', 'N/A')))
            
            # Update achievements
            self.info_widgets['badges']['value'].config(text=str(additional_info.get('badges_count', 'N/A')))
            self.info_widgets['groups']['value'].config(text=str(additional_info.get('groups_count', 'N/A')))
            
            # Update presence
            self.info_widgets['status']['value'].config(text=str(additional_info.get('presence', 'N/A')))
            current_game = additional_info.get('current_game', 'N/A')
            self.info_widgets['current_game']['value'].config(text=str(current_game))
            self.info_widgets['last_location']['value'].config(text=str(additional_info.get('last_location', 'N/A')))
            
            # Update owned groups
            owned_groups = additional_info.get('owned_groups', [])
            if owned_groups:
                groups_text = "\n".join([f"• {g['name']} (ID: {g['id']}, Members: {g['member_count']})" 
                                       for g in owned_groups[:10]])
                if len(owned_groups) > 10:
                    groups_text += f"\n... and {len(owned_groups) - 10} more"
            else:
                groups_text = "None"
            self.info_widgets['owned_groups']['value'].config(text=groups_text)
            
            # Update owned games
            owned_games = additional_info.get('owned_games', [])
            if owned_games:
                games_text = "\n".join([f"• {g['name']} (ID: {g['id']}, Visits: {g['visits']:,}, Playing: {g['playing']})" 
                                       for g in owned_games[:10]])
                if len(owned_games) > 10:
                    games_text += f"\n... and {len(owned_games) - 10} more"
            else:
                games_text = "None"
            self.info_widgets['owned_games']['value'].config(text=games_text)
            
            # Update alt accounts
            alt_accounts = additional_info.get('alt_accounts', [])
            if alt_accounts:
                alts_text = "\n".join([f"• {alt['username']} (ID: {alt['id']}, Score: {alt['score']}/10)" 
                                      for alt in alt_accounts])
                alts_text += "\n\nReasons:\n" + "\n".join([f"  - {alt['username']}: {', '.join(alt['reasons'][:2])}" 
                                                          for alt in alt_accounts[:5]])
            else:
                alts_text = "None detected"
            self.info_widgets['alt_accounts']['value'].config(text=alts_text)
            
            # Update links
            user_id = user_info.get('id', 'N/A')
            profile_url = f"https://www.roblox.com/users/{user_id}/profile"
            avatar_url_link = f"https://www.roblox.com/users/{user_id}/avatar"
            
            self.info_widgets['profile_link']['value'].config(text=profile_url)
            self.info_widgets['profile_link']['value'].bind("<Button-1>", lambda e: self._open_url(profile_url))
            
            self.info_widgets['avatar_link']['value'].config(text=avatar_url_link)
            self.info_widgets['avatar_link']['value'].bind("<Button-1>", lambda e: self._open_url(avatar_url_link))
            
            self._update_status("✓ Information loaded successfully!")
            
        except Exception as e:
            self._show_error(f"Error updating UI: {str(e)}")
        finally:
            self.search_button.config(state=tk.NORMAL)
    
    def _open_url(self, url):
        """Open URL in default browser"""
        webbrowser.open(url)
    
    def format_date(self, date_string):
        """Format ISO date string to readable format"""
        if not date_string:
            return "N/A"
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            return date_string
    
    def use_current_game_id(self):
        """Extract universe ID from current game and fill it in"""
        current_game_text = self.info_widgets.get('current_game', {}).get('value', None)
        if current_game_text:
            text = current_game_text.cget('text')
            # Extract universe ID from text like "Game Name (Universe: 123456)"
            match = re.search(r'Universe:\s*(\d+)', text)
            if match:
                universe_id = match.group(1)
                self.game_id_entry.delete(0, tk.END)
                self.game_id_entry.insert(0, universe_id)
                messagebox.showinfo("Success", f"Game ID set to {universe_id}")
            else:
                messagebox.showwarning("Warning", "Could not extract Universe ID from current game. Please enter it manually.")
        else:
            messagebox.showwarning("Warning", "No current game information available. Please search for a user first.")
    
    def search_user_in_servers(self):
        """Search for the current user in game servers"""
        game_id = self.game_id_entry.get().strip()
        if not game_id:
            messagebox.showwarning("Warning", "Please enter a Game ID (Universe ID)")
            return
        
        # Get the user ID from the last search
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showwarning("Warning", "Please search for a user first")
            return
        
        # Disable button and show loading
        self.search_servers_button.config(state=tk.DISABLED)
        self.info_widgets['server_search_result']['value'].config(text="Searching servers... This may take a while...")
        self.root.update()
        
        # Fetch in a separate thread
        thread = threading.Thread(target=self._search_servers_thread, args=(game_id, username))
        thread.daemon = True
        thread.start()
    
    def _search_servers_thread(self, game_id, username):
        """Search servers in a separate thread"""
        try:
            # Get user ID
            user_id = self.get_user_id(username)
            if not user_id:
                self.root.after(0, lambda: self._update_server_result(f"Error: User '{username}' not found"))
                return
            
            # Get game servers
            self.root.after(0, lambda: self.info_widgets['server_search_result']['value'].config(
                text="Fetching server list..."))
            
            servers = self.get_game_servers(game_id)
            if not servers:
                self.root.after(0, lambda: self._update_server_result("No servers found or error fetching servers"))
                return
            
            total_servers = len(servers)
            self.root.after(0, lambda: self.info_widgets['server_search_result']['value'].config(
                text=f"Found {total_servers} servers. Checking player lists..."))
            
            # First, verify user is actually in this game using presence API
            presence_info = self.check_user_presence_in_game(user_id, game_id)
            user_in_game = presence_info and presence_info.get('in_game')
            
            if not user_in_game:
                self.root.after(0, lambda: self._update_server_result(
                    f"✗ User is not currently playing this game (Universe ID: {game_id})"))
                return
            
            # Check each server for the user
            found_servers = []
            checked = 0
            
            for server in servers:
                checked += 1
                if checked % 5 == 0:
                    self.root.after(0, lambda c=checked, t=total_servers: 
                        self.info_widgets['server_search_result']['value'].config(
                            text=f"Checked {c}/{t} servers..."))
                
                server_id = server.get('id')
                server_token = server.get('token')  # Some APIs use token instead of id
                
                # Check if user is in this server using multiple methods
                user_found = False
                
                # Method 1: Check playerTokens - these might be user IDs or session tokens
                player_tokens = server.get('playerTokens', [])
                if player_tokens:
                    # playerTokens could be:
                    # 1. Direct user IDs (as integers)
                    # 2. Session tokens (strings) that need resolution
                    # 3. User IDs as strings
                    for token in player_tokens:
                        try:
                            # Try direct integer comparison
                            if isinstance(token, int) and token == int(user_id):
                                user_found = True
                                break
                            # Try string to int conversion
                            elif isinstance(token, str) and token.isdigit():
                                if int(token) == int(user_id):
                                    user_found = True
                                    break
                            # Try as string comparison
                            elif str(token) == str(user_id):
                                user_found = True
                                break
                        except (ValueError, TypeError):
                            # If token format is unexpected, try to resolve it
                            resolved_id = self.resolve_player_token(token)
                            if resolved_id and int(resolved_id) == int(user_id):
                                user_found = True
                                break
                
                # Method 2: Check if server data includes player list with user IDs
                if not user_found:
                    player_list = server.get('players', [])
                    if player_list:
                        for player in player_list:
                            # Try different possible keys for user ID
                            player_id = (player.get('id') or 
                                       player.get('userId') or 
                                       player.get('user_id') or
                                       player.get('Id'))
                            if player_id and str(player_id) == str(user_id):
                                user_found = True
                                break
                
                # Method 3: Try to get players from server endpoint
                if not user_found and (server_id or server_token):
                    players = self.get_server_players(server_id or server_token, game_id)
                    if players:
                        for player in players:
                            # Handle both dict and direct ID formats
                            if isinstance(player, dict):
                                player_id = (player.get('id') or 
                                           player.get('userId') or 
                                           player.get('user_id') or
                                           player.get('Id'))
                            else:
                                # If player is just an ID/token
                                player_id = player
                            
                            if player_id and str(player_id) == str(user_id):
                                user_found = True
                                break
                
                # Method 4: Try to use game place endpoint to get player info
                # Some games expose player data through their place page
                if not user_found and (server_id or server_token):
                    place_players = self.get_place_players(game_id, server_id or server_token)
                    if place_players:
                        for player in place_players:
                            player_id = (player.get('id') or 
                                       player.get('userId') or 
                                       player.get('user_id'))
                            if player_id and str(player_id) == str(user_id):
                                user_found = True
                                break
                
                if user_found:
                    found_servers.append({
                        'server_id': server_id or server_token or 'N/A',
                        'player_count': server.get('playing', server.get('playerCount', 0)),
                        'max_players': server.get('maxPlayers', server.get('maxPlayers', 'N/A')),
                        'fps': server.get('fps', 'N/A'),
                        'ping': server.get('ping', 'N/A')
                    })
            
            # Update result
            if found_servers:
                result_text = f"✓ Found user in {len(found_servers)} server(s):\n\n"
                for i, server in enumerate(found_servers, 1):
                    result_text += f"Server {i}:\n"
                    result_text += f"  • Server ID: {server['server_id']}\n"
                    result_text += f"  • Players: {server['player_count']}/{server['max_players']}\n"
                    result_text += f"  • FPS: {server['fps']}\n"
                    result_text += f"  • Ping: {server['ping']}\n\n"
            else:
                # Alternative approach: If user is confirmed in game, show all servers as potential matches
                if user_in_game and total_servers > 0:
                    result_text = f"⚠ User is confirmed to be in this game (Universe ID: {game_id})\n"
                    result_text += f"but Roblox API doesn't provide player lists for privacy reasons.\n\n"
                    result_text += f"Found {total_servers} public server(s). User is likely in one of these:\n\n"
                    
                    for i, server in enumerate(servers[:10], 1):  # Show first 10 servers
                        server_id = server.get('id') or server.get('token') or 'N/A'
                        player_count = server.get('playing', server.get('playerCount', 0))
                        max_players = server.get('maxPlayers', 'N/A')
                        result_text += f"Server {i}:\n"
                        result_text += f"  • Server ID: {server_id}\n"
                        result_text += f"  • Players: {player_count}/{max_players}\n"
                        if server.get('fps'):
                            result_text += f"  • FPS: {server.get('fps')}\n"
                        result_text += "\n"
                    
                    if total_servers > 10:
                        result_text += f"... and {total_servers - 10} more servers\n\n"
                    
                    result_text += "Note: Due to API limitations, we cannot determine which exact server.\n"
                    result_text += "The user is confirmed to be in this game and is likely in one of the above servers."
                else:
                    result_text = f"✗ User not found in any of the {total_servers} checked servers.\n\n"
                    if user_in_game:
                        result_text += f"Note: User is confirmed to be in this game (Universe ID: {game_id}), "
                        result_text += "but could not be found in public server player lists.\n"
                        result_text += "Possible reasons:\n"
                        result_text += "  • User is in a private/VIP server\n"
                        result_text += "  • Roblox API doesn't provide full player lists for privacy\n"
                        result_text += "  • Server player data format differs from expected\n"
                    else:
                        result_text += "Note: The user might be in a private server, or the server list may be incomplete."
            
            self.root.after(0, lambda: self._update_server_result(result_text))
            
        except Exception as e:
            self.root.after(0, lambda: self._update_server_result(f"Error: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.search_servers_button.config(state=tk.NORMAL))
    
    def _update_server_result(self, text):
        """Update server search result"""
        self.info_widgets['server_search_result']['value'].config(text=text)
    
    def get_game_servers(self, universe_id):
        """Get list of public servers for a game"""
        servers = []
        try:
            url = f"https://games.roblox.com/v1/games/{universe_id}/servers/Public"
            params = {
                "sortOrder": "Asc",
                "limit": "100"  # Get up to 100 servers
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                servers = data.get('data', [])
                # Debug: Print first server structure to understand data format
                if servers and len(servers) > 0:
                    print(f"DEBUG: First server structure keys: {servers[0].keys()}")
                    print(f"DEBUG: First server playerTokens type: {type(servers[0].get('playerTokens'))}")
        except Exception as e:
            print(f"Error getting game servers: {e}")
        return servers
    
    def get_server_players(self, server_id, universe_id=None):
        """Get list of players in a specific server"""
        try:
            # Try different possible endpoints
            endpoints = []
            if universe_id:
                endpoints.append(f"https://games.roblox.com/v1/games/{universe_id}/servers/{server_id}")
            endpoints.extend([
                f"https://games.roblox.com/v1/games/servers/{server_id}",
                f"https://games.roblox.com/v1/games/{server_id}/servers",
            ])
            
            for url in endpoints:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        # Try different possible keys for player data
                        players = (data.get('players') or 
                                 data.get('data', {}).get('players') or
                                 data.get('playerTokens') or
                                 data.get('data', {}).get('playerTokens') or
                                 [])
                        if players:
                            return players if isinstance(players, list) else []
                except:
                    continue
        except Exception as e:
            print(f"Error getting server players: {e}")
        return None
    
    def resolve_player_token(self, token):
        """Try to resolve a player token to a user ID"""
        # Player tokens might already be user IDs, or we might need to resolve them
        # For now, return the token as-is if it looks like a number
        try:
            if isinstance(token, (int, str)) and str(token).isdigit():
                return int(token)
        except:
            pass
        return None
    
    def check_user_presence_in_game(self, user_id, universe_id):
        """Check if user is currently in a specific game"""
        try:
            url = f"https://presence.roblox.com/v1/presence/users"
            payload = {"userIds": [user_id]}
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                presence_data = response.json().get('userPresences', [])
                if presence_data:
                    presence = presence_data[0]
                    # Check if user is in the game (universeId matches)
                    if str(presence.get('universeId')) == str(universe_id):
                        return {'in_game': True, 'presence': presence}
        except Exception as e:
            print(f"Error checking presence: {e}")
        return None
    
    def get_place_players(self, universe_id, server_id):
        """Try to get players from game place endpoint (alternative method)"""
        try:
            # Try to get place ID from universe
            url = f"https://games.roblox.com/v1/games?universeIds={universe_id}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json().get('data', [])
                if data:
                    place_id = data[0].get('rootPlaceId')
                    if place_id:
                        # Try to get player info from place (this may not work due to privacy)
                        place_url = f"https://www.roblox.com/games/{place_id}"
                        # Note: This would require web scraping which violates ToS
                        # So we'll skip this approach
                        pass
        except Exception as e:
            print(f"Error getting place players: {e}")
        return None
    
    def _show_error(self, message):
        """Show error message"""
        self._update_status("✗ Error occurred", is_warning=True)
        self.search_button.config(state=tk.NORMAL)
        messagebox.showerror("Error", message)


def main():
    root = tk.Tk()
    app = RobloxUserInfoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
