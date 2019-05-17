# -*- coding: utf-8 -*-
"""
Author: TruongNV
Created Date: 17/05/2019
Describe:
"""
import os

import random

import pandas
from datetime import datetime

DATE_TIME_ORDER_FORMAT = "%m-%d-%Y %H:%M:%S"


class Domain(object):
    @staticmethod
    def get_stt_order():
        working_dir = os.getcwd()
        file_order = working_dir + "/Input_order_lists.csv"
        file_sup_prior = working_dir + "/Input_supplier_priority.csv"
        file_sup_stock = working_dir + "/Input_supplier_stock.csv"

        data_order = pandas.read_csv(file_order)
        data_prior = pandas.read_csv(file_sup_prior)
        data_stock = pandas.read_csv(file_sup_stock)

        data_order.dropna(inplace=True, how='all')
        data_prior.dropna(inplace=True, how='all')
        data_stock.dropna(inplace=True, how='all')

        data_order = data_order.fillna("")
        data_prior = data_prior.fillna(0)
        data_stock = data_stock.fillna(0)

        suppliers = set(data_prior.columns)
        suppliers.discard("SKU")
        suppliers.discard("Tên viết tắt")

        # ================================
        #  data_prior
        # ================================
        prior = get_prior(data_prior)

        # ================================
        #  data_stock
        # ================================
        stock = get_stock(data_stock)

        # ================================
        #  Processing Order
        # ================================
        error_order = list()
        success_orders = list()
        for row in data_order.index:
            row_data = data_order.loc[row].to_dict()

            # get data
            quantity = row_data.get("Quantity")
            line_item_sku = row_data.get("Lineitem SKU")

            # processing:
            quantity = int(quantity) if quantity else 0

            # Truong hop loi nhap lieu quantity == 0
            if not quantity:
                # xu ly nhu error_order.csv
                error_order.append(row_data)
                continue

            # check sku have in stock
            stock_sku_data = stock.get(line_item_sku)

            if not stock_sku_data:
                # xu ly nhu error_order.csv
                error_order.append(row_data)
                continue

            # process when in stock
            stock_sku_data = stock.get(line_item_sku)

            # get prior supplier
            prior_sku_data = prior.get(line_item_sku)
            sort_name_sku = prior_sku_data.get("shorted_name")
            prior_supplier_sku = prior_sku_data.get("prior")
            un_prior_supp_sku = prior_sku_data.get("un_prior")

            prior_stock_exist = get_prior_stock_exist(stock_sku_data, prior_supplier_sku)
            un_prior_stock_exist = get_un_prior_stock_exist(stock_sku_data, un_prior_supp_sku)

            data_fine = get_data_fine(prior_stock_exist, un_prior_stock_exist, stock_sku_data, quantity)
            if len(data_fine) <= 0:
                # xu ly nhu error_order.csv
                error_order.append(row_data)
                continue
            else:
                row_data.update({"supp_info": data_fine})
                row_data.update({"sort_name_sku": sort_name_sku})
                success_orders.append(row_data)

        print("success_orders: {}".format(success_orders))
        print("error_order: {}".format(error_order))

        return success_orders, error_order

    @staticmethod
    def report_err(err_result):
        # convert to pandas df
        df = pandas.DataFrame(err_result)

        # sap xep lai thu tu column
        df = df[[
            "Order ID",
            "Order Name",
            "Order Status",
            "Last Fulfill Date",
            "Tracking Number",
            "Notes",
            "Paid_at",
            "Processed at",
            "Order Created At",
            "Quantity",
            "Lineitem SKU",
            "Shipping Company Name",
            "Replace at"
        ]]

        df.to_csv("error_order.csv")

    @staticmethod
    def report_success(success_result):
        # create folder to report
        working_dir = os.getcwd()
        now = datetime.now()
        DATE_REPORT = "%d-%m-%Y"
        PROCESSING_DATE = "%d.%m"
        report_folder = now.strftime(DATE_REPORT)
        processing_date = now.strftime(PROCESSING_DATE)
        report_folder = working_dir + "/" + report_folder
        if not os.path.exists(report_folder):
            os.makedirs(report_folder)

        print(report_folder)
        print("=====================")
        for data in success_result:
            supp_info = data.get("supp_info")
            sort_name_sku = data.get("sort_name_sku")
            for each in supp_info:
                folder_sup_report = report_folder + "/" + each
                number_of_pcs = supp_info[each]
                supp_name = each.replace(" ", "_")
                file_name = "{}_{}_{}_{}.csv".format(sort_name_sku, number_of_pcs, processing_date, supp_name)
                file_path = folder_sup_report + "/" + file_name
                if now.strftime("%p") == "PM":
                    a_or_b = "b"
                else:
                    a_or_b = "a"
                status = "P {} {} {}".format(a_or_b, processing_date, supp_name)

                data_str = ""
                data_str += data["Order ID"]
                data_str += "," + data["Order Name"]
                data_str += "," + data["Tracking Number"]
                data_str += "," + data["Notes"]
                data_str += "," + data["Paid_at"]
                data_str += "," + str(number_of_pcs)
                data_str += "," + str(sort_name_sku)
                data_str += "," + str(status) + "\n"

                if not os.path.exists(folder_sup_report):
                    os.makedirs(folder_sup_report)
                if os.path.exists(file_path):
                    with open(file_path, 'a+') as f:
                        f.write(data_str)
                        f.close()
                else:
                    with open(file_path, 'a+') as f:
                        f.write("Order ID,Order Name,Tracking Number,Notes,Paid_at,Quatity,Product Name,Status\n")
                        f.write(data_str)
                        f.close()


def get_prior(data_prior):
    prior = dict()
    for row in data_prior.index:
        row_data = data_prior.loc[row].to_dict()

        sku = row_data.get("SKU")
        shorted_name = row_data.get("Tên viết tắt")

        un_prior = list()
        value_prior = dict()
        sku_prior = dict()
        for supplier_name in row_data:
            if supplier_name == "SKU" or supplier_name == "Tên viết tắt":
                continue
            if row_data[supplier_name]:
                value_prior.update({supplier_name: row_data[supplier_name]})
            else:
                un_prior.append(supplier_name)
        sku_prior.update({"un_prior": un_prior})
        sku_prior.update({"shorted_name": shorted_name})
        sku_prior.update({"prior": value_prior})
        prior.update({sku: sku_prior})
    return prior


def get_stock(data_stock):
    stock = dict()
    for row in data_stock.index:
        row_data = data_stock.loc[row].to_dict()
        sku = row_data.get("SKU")
        sku_stock = dict()
        for supplier_name in row_data:
            if supplier_name == "SKU":
                continue
            if row_data[supplier_name]:
                sku_stock.update({supplier_name: row_data[supplier_name]})
        stock.update({sku: sku_stock})
    return stock


def get_prior_stock_exist(stock_sku_data, prior_supplier_sku):
    prior_stock_exist = dict()
    for i in stock_sku_data:
        if i in prior_supplier_sku:
            prior_stock_exist.update({prior_supplier_sku[i]: i})
    return prior_stock_exist


def get_un_prior_stock_exist(stock_sku_data, un_prior_supp_sku):
    un_prior_stock_exist = dict()
    for i in stock_sku_data:
        if i in un_prior_supp_sku:
            un_prior_stock_exist.update({stock_sku_data[i]: i})
    return un_prior_stock_exist


def get_name_supp(prior_stock_exist, un_prior_stock_exist):
    if len(prior_stock_exist) > 0:
        min_prior = min(prior_stock_exist)
        name_supp = prior_stock_exist.pop(min_prior)
    else:
        if len(un_prior_stock_exist) > 0:
            name_supp = random.choice(un_prior_stock_exist)
            un_prior_stock_exist.pop(un_prior_stock_exist.index(name_supp))
        else:
            name_supp = None
    return name_supp


def get_data_fine(prior_stock_exist, un_prior_stock_exist, stock_sku_data, quantity):
    data_fine = dict()
    name_supp = get_name_supp(prior_stock_exist, un_prior_stock_exist)
    if name_supp is None:
        return None

    if name_supp is not None:
        supp_stock_exist = stock_sku_data[name_supp]
        supp_stock_handle = supp_stock_exist - quantity
        # stock_sku_data.update({name_supp: supp_stock_handle})

        if supp_stock_handle >= 0:
            # update lai so luong supp_stock_handle
            stock_sku_data.update({name_supp: supp_stock_handle})
            data_fine.update({name_supp: quantity})
            return data_fine
        else:
            quantity = 0 - supp_stock_handle
            data_fine_sub = get_data_fine(prior_stock_exist, un_prior_stock_exist, stock_sku_data, quantity)
            if data_fine_sub is None:
                return data_fine
            else:
                data_fine.update(data_fine_sub)
    return data_fine


if __name__ == '__main__':
    success, err = Domain.get_stt_order()

    # save to error_order.csv
    Domain.report_err(err)

    # save success result
    Domain.report_success(success)
