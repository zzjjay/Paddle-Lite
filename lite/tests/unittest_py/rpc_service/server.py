import rpyc
from rpyc.utils.server import ThreadedServer
from paddlelite.lite import *

rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True

class RPCService(rpyc.Service):
    def exposed_run_lite_model(self, model, params,inputs):
        '''
        Test a single case.
        '''
        valid_places=[Place(TargetType.ARM, PrecisionType.FP32)]
        config = CxxConfig()
        config.set_valid_places(valid_places)
        config.set_model_buffer(model, len(model), params, len(params))
        predictor = create_paddle_predictor(config)
        for name in inputs:
            input_tensor = predictor.get_input_by_name(name)
            input_tensor.from_numpy(inputs[name]['data'])
            if inputs[name]['lod'] is not None:
                input_tensor.set_lod(inputs[name]['lod'])
        predictor.run()
        result = {}
        for out_name in predictor.get_output_names():
            result[out_name] = predictor.get_output_by_name(out_name).numpy()
        return result


if __name__ == "__main__":
    server = ThreadedServer(RPCService, port =18812, protocol_config = rpyc.core.protocol.DEFAULT_CONFIG)
    server.start()