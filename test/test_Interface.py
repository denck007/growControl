import unittest

from growControl import Interface, GrowObject


class test_Interface(unittest.TestCase):
    '''
    Test the growControl.Interface functionality
    '''

    def test_init(self):
        '''
        Test the basic initialization of an object
        '''
        params = {"name":"test_object1",
                    "time_warmup":1,
                    "time_run_every":1,
                    "interface":{"interface_type":"csv", 
                                "fname":"testing_csv_file.csv",
                                "interface_mode":'output'
                                }
                    }
        go_parent= "Test Parent"
        
        go = GrowObject(params,go_parent)

        self.assertEqual(go.interface.interface_type,params["interface"]["interface_type"])
        self.assertEqual(go.interface._csv_fname,params["interface"]["fname"])
        self.assertEqual(go.interface.interface_mode,params["interface"]["interface_mode"])
         

