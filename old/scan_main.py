from treelib import Tree

from old import scan_for_ids
from old import scan_for_services


def label_services_iso14229(sid):
    services_dictionary = {
        "Diagnostic Session Control": 0x10,
        "ECU Reset": 0x11,
        "Clear Diagnostic Information": 0x14,
        "Read DTC Information": 0x19,
        "Read Data by Identifier": 0x22,
        "Read Memory by Address": 0x23,
        "Read Scaling Data by Identifier": 0x24,
        "Security Access": 0x27,
        "Communication Control": 0x28,
        "Read Data by Periodic Data Identifier": 0x2A,
        "Dynamically Define Data Identifier": 0x2C,
        "Write Data by Identifier": 0x2E,
        "Input Output Control by Identifier": 0x2F,
        "Routine Control": 0x31,
        "Request Download": 0x34,
        "Request Upload": 0x35,
        "Transfer Data": 0x36,
        "Request Transfer Exit": 0x37,
        "Write Memory by Address": 0x3D,
        "Tester Present": 0x3E,
        "Access Timing Parameters": 0x83,
        "Secured Data Transmission": 0x84,
        "Control DTC Setting": 0x85,
        "Response on Event": 0x86,
        "Link Control": 0x87
    }

    for key, value in services_dictionary.items():
        if value == sid:
            return key

    return "Unknown ISO 14229 Service."


def label_services_iso14230(sid):
    services_dictionary = {
        "Start Diagnostic Session": 0x10,
        "ECU Reset": 0x11,
        "Clear Diagnostic Information": 0x14,
        "Read Status of Diagnostic Trouble Codes": 0x17,
        "Read Diagnostic Trouble Codes by Status": 0x18,
        "Read Data by Local Identifier": 0x21,
        "Read Data by Identifier": 0x22,
        "Read Memory by Address": 0x23,
        "Security Access": 0x27,
        "Disable Normal Message Transmission": 0x28,
        "Enable Normal Message Transmission": 0x29,
        "Dynamically Define Data Identifier": 0x2C,
        "Write Data by Identifier": 0x2E,
        "Input Output Control by Local Identifier": 0x30,
        "Start Routine by Local Identifier": 0x31,
        "Stop Routine by Local Identifier": 0x32,
        "Request Results by Local Identifier": 0x33,
        "Request Download": 0x34,
        "Request Upload": 0x35,
        "Transfer Data": 0x36,
        "Request Transfer Exit": 0x37,
        "Write Memory by Address": 0x3D,
        "Tester Present": 0x3E,
        "Control DTC Setting": 0x85,
        "Response on Event": 0x86,
    }

    for key, value in services_dictionary.items():
        if value == sid:
            return key

    return "Unknown ISO 14229 Service."


def label_service_10_subfunctions(sf):
    if sf == 0x00:
        return "ISO SAE Reserved"
    if sf == 0x01:
        return "Default Session"
    if sf == 0x02:
        return "Programming Session"
    if sf == 0x03:
        return "Extended Diagnostic Session"
    if sf == 0x04:
        return "Safety System Diagnostic Session"
    if 0x05 <= sf <= 0x3F:
        return "ISO SAE Reserved"
    if 0x40 <= sf <= 0x5F:
        return "Vehicle Manufacturer Specific"
    if 0x60 <= sf <= 0x7E:
        return "System Supplier Specific"
    if sf == 0x7F:
        return "ISO SAE Reserved"

    return "Undefined Subfunction"


def label_service_11_subfunctions(sf):
    if sf == 0x00:
        return "ISO SAE Reserved"
    if sf == 0x01:
        return "Hard Reset"
    if sf == 0x02:
        return "Key Off/On Reset"
    if sf == 0x03:
        return "Soft Reset"
    if sf == 0x04:
        return "Enable Rapid Power Shutdown"
    if sf == 0x05:
        return "Disable Rapid Power Shutdown"
    if 0x06 <= sf <= 0x3F:
        return "ISO SAE Reserved"
    if 0x40 <= sf <= 0x5F:
        return "Vehicle Manufacturer Specific"
    if 0x60 <= sf <= 0x7E:
        return "System Supplier Specific"
    if sf == 0x7F:
        return "ISO SAE Reserved"

    return "Undefined Subfunction"


def log_data(file_input, filename='default_log_file', mode='a', append_time_to_log_file_name=True):
    try:
        import datetime
        import time
        if append_time_to_log_file_name:
            filename += datetime.datetime.today().strftime('%Y-%m-%d-') + str(time.time()) + '.log'
        else:
            filename += '.log'
        file = open(filename, mode)
        file.write(file_input.show())
        return True
    except IOError as e:
        print("Error writing file: {}".format(e))
        return False


def run_scan(
        start_arb_id=0x000,
        end_arb_id=0x7FF,
        scan_for_services_start_service=0x10,
        scan_for_services_end_service=0xFF,
        service_10_start_subfunction=0x00,
        service_10_end_subfunction=0xFF,
        service_11_start_subfunction=0x00,
        service_11_end_subfunction=0x00,
        service_22_2e_2f_start_PID=0x0000,
        service_22_2e_2f_end_PID=0x000F,
        service_27_start_level=0x00,
        service_27_end_level=0xFF,
        socket_can_interface='can0',
        scan_fast_mode=True,
        can_scan_timeout=0.1,
        scan_for_service_subfunctions=True,
        try_twice=True,
        verbose_mode=True
):
    tp_can = socket_can_interface

    '''
    Scan for IDs.  This will try a range of IDs from `arb_id_scan_low` to `arb_id_scan_high`.
    
    `try_twice` will attempt to send and receive two times inorder to reduce false positives
    
    `verbose_mode` will print a little more information for you
    '''

    successfull_pairs = scan_for_ids(socket_can_interface,
                                     arb_id_scan_low=start_arb_id,
                                     arb_id_scan_high=end_arb_id,
                                     try_twice=try_twice,
                                     verbose_mode=verbose_mode,
                                     can_scan_timeout=can_scan_timeout,
                                     )
    scan_tree = Tree()
    scan_tree.create_node('Vehicle Network', 'vehicle_network')

    for pair in successfull_pairs:

        diagnostic_tx_arb_id, diagnostic_rx_arb_id = pair
        node_name = 'node{:03X}{:03X}'.format(diagnostic_tx_arb_id, diagnostic_rx_arb_id)
        scan_tree.create_node('{:03X} <==> {:03X} :\tScanning Services: {:02X} - {:02X}'.format(
            diagnostic_tx_arb_id,
            diagnostic_rx_arb_id,
            scan_for_services_start_service,
            scan_for_services_end_service
        ),
            node_name, parent='vehicle_network')

        '''
        Check the Services that are supported
        '''

        supported_services = scan_for_services(diagnostic_tx_arb_id=diagnostic_tx_arb_id,
                                               diagnostic_rx_arb_id=diagnostic_rx_arb_id,
                                               start_service_id=scan_for_services_start_service,
                                               end_service_id=scan_for_services_end_service,
                                               can_socket=socket_can_interface)

        '''
        Check Subfunctions for Supported Services :
        '''

        for supported_service in supported_services:
            service_label = label_services_iso14229(supported_service)
            scan_tree.create_node('{:02X}: {}'.format(supported_service, service_label),
                                  '{}_service_{:02X}'.format(node_name, supported_service), parent=node_name)

            if scan_for_service_subfunctions:

                if supported_service == 0x10:
                    pos_10, neg_10 = scan_for_service_10(pair, tp_can, start_sub_function=service_10_start_subfunction,
                                                         end_sub_function=service_10_end_subfunction)
                    for subs, data in pos_10:
                        subfunction_label = label_service_10_subfunctions(subs)
                        scan_tree.create_node('{:02X}: {}'.format(subs, subfunction_label),
                                              '{}_{:02X}_subfunction{:02X}'.format(node_name, supported_service, subs),
                                              parent='{}_service_{:02X}'.format(node_name, supported_service))

                elif supported_service == 0x11:
                    pos_11, neg_11 = scan_for_service_11(pair, tp_can, start_sub_function=service_11_start_subfunction,
                                                         end_sub_function=service_11_end_subfunction)
                    for subs, data in pos_11:
                        subfunction_label = label_service_11_subfunctions(subs)
                        scan_tree.create_node('{:02X}: {}'.format(subs, subfunction_label),
                                              '{}_{:02X}_subfunction{:02X}'.format(node_name, supported_service, subs),
                                              parent='{}_service_{:02X}'.format(node_name, supported_service))

                elif supported_service == 0x22:
                    pos_22, neg_22 = scan_for_service_22(pair, tp_can, start_sub_function=service_22_2e_2f_start_PID,
                                                         end_sub_function=service_22_2e_2f_end_PID)
                    for subs, data in pos_22:
                        scan_tree.create_node(
                            '{:04X}: {}'.format(subs, (data.hex() if data is not None else 'No Data')),
                            '{}_{:02X}_subfunction{:02X}'.format(node_name, supported_service, subs),
                            parent='{}_service_{:02X}'.format(node_name, supported_service))

                elif supported_service == 0x27:
                    if service_27_start_level & 0x01 != 1:
                        service_27_start_level += 1

                    pos_27, neg_27 = scan_for_service_27(pair, tp_can, start_sub_function=service_27_start_level,
                                                         end_sub_function=service_27_end_level)
                    for subs, data in pos_27:
                        scan_tree.create_node(
                            '{:02X}: {}'.format(subs, (data.hex() if data is not None else 'No Data')),
                            '{}_{:02X}_subfunction{:02X}'.format(node_name, supported_service, subs),
                            parent='{}_service_{:02X}'.format(node_name, supported_service))

                elif supported_service == 0x2E:

                    pos_2e, neg_2e = scan_for_service_2e(pair, tp_can, start_sub_function=service_22_2e_2f_start_PID,
                                                         end_sub_function=service_22_2e_2f_end_PID)
                    for subs, data in pos_2e:
                        scan_tree.create_node(
                            '{:04X}: {}'.format(subs, (data.hex() if data is not None else 'No Data')),
                            '{}_{:02X}_subfunction{:02X}'.format(node_name, supported_service, subs),
                            parent='{}_service_{:02X}'.format(node_name, supported_service))

                elif supported_service == 0x2F:

                    pos_2e, neg_2e = scan_for_service_2f(pair, tp_can, start_sub_function=service_22_2e_2f_start_PID,
                                                         end_sub_function=service_22_2e_2f_end_PID)
                    for subs, data in pos_2e:
                        scan_tree.create_node(
                            '{:04X}: {}'.format(subs, (data.hex() if data is not None else 'No Data')),
                            '{}_{:02X}_subfunction{:02X}'.format(node_name, supported_service, subs),
                            parent='{}_service_{:02X}'.format(node_name, supported_service))

    return scan_tree
