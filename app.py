import hashlib
import hmac
import os
import re
import sqlite3

import streamlit as st


DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")


def connect_db():
	connection = sqlite3.connect(DATABASE)
	connection.row_factory = sqlite3.Row
	return connection


def initialize_db():
	with connect_db() as connection:
		connection.execute(
			"""CREATE TABLE IF NOT EXISTS users (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				username TEXT NOT NULL COLLATE NOCASE UNIQUE,
				email TEXT NOT NULL COLLATE NOCASE UNIQUE,
				password_hash TEXT NOT NULL,
				salt TEXT NOT NULL,
				created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
			)"""
		)


def hash_password(password, salt=None):
	salt = salt or os.urandom(16).hex()
	digest = hashlib.pbkdf2_hmac(
		"sha256", password.encode("utf-8"), bytes.fromhex(salt), 200_000
	).hex()
	return digest, salt


def create_user(username, email, password):
	password_hash, salt = hash_password(password)
	try:
		with connect_db() as connection:
			connection.execute(
				"INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)",
				(username.strip(), email.strip(), password_hash, salt),
			)
		return True
	except sqlite3.IntegrityError:
		return False


def verify_user(username, password):
	with connect_db() as connection:
		user = connection.execute(
			"SELECT id, username, password_hash, salt FROM users WHERE username = ?",
			(username.strip(),),
		).fetchone()
	if user is None:
		return None
	candidate, _ = hash_password(password, user["salt"])
	if hmac.compare_digest(candidate, user["password_hash"]):
		return {"id": user["id"], "username": user["username"]}
	return None


def registration_form():
	with st.form("registration_form"):
		username = st.text_input("Username").strip()
		email = st.text_input("Email address").strip()
		password = st.text_input("Password", type="password")
		confirmation = st.text_input("Confirm password", type="password")
		submitted = st.form_submit_button("Create account", use_container_width=True)

	if not submitted:
		return
	if not username or not email or not password:
		st.error("Please complete every field.")
	elif len(username) < 3:
		st.error("Username must be at least 3 characters.")
	elif not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
		st.error("Enter a valid email address.")
	elif len(password) < 8:
		st.error("Password must be at least 8 characters.")
	elif password != confirmation:
		st.error("Passwords do not match.")
	elif create_user(username, email, password):
		st.success("Account created. Select Log in to continue.")
	else:
		st.error("That username or email is already registered.")


def login_form():
	with st.form("login_form"):
		username = st.text_input("Username")
		password = st.text_input("Password", type="password")
		submitted = st.form_submit_button("Log in", use_container_width=True)

	if submitted:
		user = verify_user(username, password) if username and password else None
		if user:
			st.session_state["user"] = user
			st.rerun()
		st.error("Enter valid login details.")


def main():
	st.set_page_config(page_title="Account Portal", page_icon="🔐")
	initialize_db()
	st.title("Account Portal")

	user = st.session_state.get("user")
	if user:
		st.success(f"Logged in as {user['username']}.")
		if st.button("Log out"):
			del st.session_state["user"]
			st.rerun()
		return

	login_tab, register_tab = st.tabs(["Log in", "Register"])
	with login_tab:
		login_form()
	with register_tab:
		registration_form()


if __name__ == "__main__":
	main()
