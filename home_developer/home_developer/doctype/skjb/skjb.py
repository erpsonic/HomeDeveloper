# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SKJB(Document):
	def validate(self):
		self.check_kavling()
		self.change_kavling()
		if self.workflow_state == "Pindah Kavling" or self.workflow_state == "Batal" :
			self.delete_kavling()
	
	def on_trash(self):
		self.delete_kavling()
	
	def on_cancel(self):
		self.delete_kavling()
	
	def autoname(self):
		self.name = self.nama_pembeli + "-" + self.perumahan + "-" + self.kavling
	
	def generate_print_number(self):
		count = frappe.get_doc("Number Count","SKJB")
		digit = str(count.next_digit)
		while len(digit) < 4 :
			digit = "0" + digit
		
		singkatan = self.kavling
		date = frappe.utils.today()
		month = date[5:7]
		year = date[0:4]
		self.print_number = digit + '/SKPJB/' + singkatan + '/' + month + '/' + year
		
		#update number count
		temp = count.next_digit + 1
		if temp > 9999 :
			temp = 1
		count.next_digit = temp
		count.save()
		
	
	def check_kavling(self):
		kavling = self.kavling
		kdoc = ""
		try :
			kdoc = frappe.get_doc("Kavling",kavling)
		except :
			frappe.throw("Kavling tidak ditemukan.")
		if kdoc.is_used and kdoc.skjb != self.name :
			frappe.throw("Kavling sudah digunakan di SKJB lain")
		
	def change_kavling(self):
		kdoc = frappe.get_doc("Kavling",self.kavling)
		kdoc.is_used = 1
		kdoc.skjb = self.name
		kdoc.save()
		
		result = frappe.db.sql(""" SELECT k.`name` FROM `tabKavling`k WHERE k.`skjb`="{0}" AND k.`name` != "{1}" """.format(self.name,self.kavling),as_list=1)
		for res in result :
			resdoc = frappe.get_doc("Kavling",res[0])
			resdoc.is_used = 0
			resdoc.skjb = ""
			resdoc.save()
	
	def delete_kavling(self):
		result = frappe.db.sql(""" SELECT k.`name` FROM `tabKavling`k WHERE k.`skjb`="{0}" """.format(self.name),as_list=1)
		for res in result :
			resdoc = frappe.get_doc("Kavling",res[0])
			resdoc.is_used = 0
			resdoc.skjb = ""
			resdoc.save()
	
	
	#dummied
	def set_kavling(self):
		kavling = self.kavling
		kdoc = frappe.get_doc("Kavling",kavling)
		kdoc.is_used = 1
		kdoc.save()
	
	#dummied
	def cancel_kavling(self):
		kavling = self.kavling
		kdoc = frappe.get_doc("Kavling",kavling)
		kdoc.is_used = 0
		kdoc.save()
		
@frappe.whitelist()
def get_sales(customer):
	cdoc = frappe.get_doc("Customer",customer)
	lead = cdoc.lead_name
	if lead :
		ldoc = frappe.get_doc("Lead",lead)
		if ldoc.lead_owner :
			return ldoc.lead_owner
		else :
			return ""
	return ""
	

@frappe.whitelist()
def make_invoice(cdn,nama_pembeli,company):
	source_dt = frappe.get_doc("SKJB Item",cdn)
	dt = frappe.new_doc('Sales Invoice')
	dt.customer = nama_pembeli
	dt.company = company
	dt.debit_to = frappe.get_value("Company",dt.company,"default_receivable_account")
	cd = dt.append('items')
	cd.item_code = "Cicilan"
	cd.rate = source_dt.jumlah_cicilan
	cd.qty = 1
	data[res[0]] = dt.name
	return dt

@frappe.whitelist()
def get_harga_by_type(type,kavling) :
	kav_doc = frappe.get_doc("Kavling",kavling)
	pr = 0
	if type == "KPR" :
		pr = kav_doc.kpr
	elif type == "Cash Keras" :
		pr = kav_doc.cash_keras
	elif type == "Tunai Bertahap" :
		pr = kav_doc.tunai_bertahap
	return pr

@frappe.whitelist()
def fetch_customer_data(customer):
	cusdoc = frappe.get_doc("Customer",customer)
	r = {}
	r["ktp_pembeli"] = cusdoc.ktp_pembeli
	r["alamat_ktp"] = cusdoc.alamat_ktp
	r["alamat_tt"] = cusdoc.alamat_tt
	r["rt_rw"] = cusdoc.rt_rw
	r["desa_kelurahan"] = cusdoc.desa_kelurahan
	r["kecamatan"] = cusdoc.kecamatan
	r["alamat_surat"] = cusdoc.alamat_surat
	r["telp_rumah"] = cusdoc.telp_rumah
	r["telp_hp"] = cusdoc.telp_hp
	r["telp_saudara"] = cusdoc.telp_saudara
	return r