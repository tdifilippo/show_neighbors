""" show_neighbors.py
    This python script utilizes pycsco lib to display LLDP neighbors info

    This will run on the jump host

    device              ip address
    Jump host         85.190.181.105
    nxos-spine1     85.190.177.249
    nxos-spine2     153.92.37.42
    nxos-leaf1       85.190.176.221
    nxos-leaf2       85.190.177.187
"""

# Standard libs
import json 

# import pycsco 
from pycsco.nxos.device import Device

def parse_config(config_body, cnt):
    """ parse_config - parses the config  'body' returned from switch.config_list

        Inputs:
            config_body (str) - The config 'body'
            cnt (int) - Number of neighbors

        Outputs:
            config_list (list) - A list of lists
    """
    # Create a list of the data split via newline
    c_list = config_body.split('\n')
    # Strip the whitespace
    clean_list = [c.strip() for c in c_list]
    # Create c_list
    c_list = []
    # Get rid of all multiple spaces to single space, in 4th to 4+cnt lists
    for clist in clean_list[4:4+cnt]:
        #clist.split()
        c_list.append(clist.split())
    # Debug, display list
    # print 'c_list %s' % c_list
    return c_list

def get_lldp_neighbor(ip, username, password):
    """ get_lldp_neighbor - retreives lldp neighbor information from pycsco library

        Inputs:
            ip (str) The dotted ip address represented as a string
            username (str) The username for ip
            password (str) The password for this username

        Outputs:
            neigh_count (int) The number of neightbors
            list_dict (list of neigh_count) The info dictionary list
            config_list (list of list) The config info (Device, local_interface, remote_interface)

    """
    switch = Device(ip=ip,username=username,password=password)

    # Show neighbors, return json
    lldp_info = switch.show('show lldp neighbors', fmat='json')
    # load data dict
    lldp_dict =json.loads(lldp_info[1])
    # Get count
    neigh_count  = lldp_dict['ins_api']['outputs']['output']['body']['neigh_count']
    list_dict = lldp_dict['ins_api']['outputs']['output']['body']['TABLE_nbor']['ROW_nbor']

    # get lldp_config info in json format
    lldp_config = switch.config('show lldp neighbors', fmat='json')
    # Load a json dictionary
    config_dict = json.loads(lldp_config[1])
    #print 'Config ip %s \n= %s' %(ip,config_dict)
    config_list = parse_config(config_dict['ins_api']['outputs']['output']['body'], neigh_count)

    # Return it
    return (neigh_count, list_dict, config_list)
 
def get_net2code_neighbors():
    config={'ip':('85.190.177.249','153.92.37.42','85.190.176.221','85.190.177.187'),
            'name':('nxos-spine1','nxos-spine2','nxos-leaf1','nxos-leaf2'),
            'username':'ntc',
            'password':'ntc123'}
    # Create a new dict
    output_dict = {}
    # iterate through the switches
    for switches in range(len(config['ip'])):
        # Read lldp neighbor from Cisco
        count, list_dict, config_list = get_lldp_neighbor(config['ip'][switches], config['username'], config['password'])
        # Create empty output_list
        output_list = []

        # Add a dictionary for each row this switch returns,appending a dictionary to the output_list
        for row in range(count):
            # Load up the row_dict for item row
            row_dict= list_dict[row]
            # Build output
            output_info={'local_interface':row_dict['port_id'],'neighbor':row_dict['chassis_id']}
            # Add neighbor_interface, using the config info in config_list
            for config_l in config_list:
                # find the neighbor_interface for this neighbor
                if output_info['local_interface'] == config_l[4] and output_info['neighbor']  == config_l[0]:
                    # append neighbor with '.ntc.com'
                    output_info['neighbor_interface'] = config_l[1]
                    output_info['neighbor'] += '.ntc.com'
            # Add  this dictionary to output_list
            output_list.append(output_info)
        output_dict[config['name'][switches]]  = output_list
    return (output_dict)



# Jump to main
if __name__ == '__main__':
    ret_dict = get_net2code_neighbors()
    print ret_dict


