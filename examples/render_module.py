from json_module import JsonModule,ModuleParameters
import marshmallow as mm
import renderapi

class RenderClientParameters(ModuleParameters):
    host = mm.fields.Str(required=True,metadata={'description':'render host'})
    port = mm.fields.Int(required=True,metadata={'description':'render post integer'})
    owner = mm.fields.Str(required=True,metadata={'description':'render default owner'})
    project = mm.fields.Str(required=True,metadata={'description':'render default project'})
    client_scripts = mm.fields.Str(required=True,metadata={'description':'path to render client scripts'})

class RenderParameters(ModuleParameters):
    render = mm.fields.Nested(RenderClientParameters)

class RenderModule(JsonModule):
    def __init__(self,*args,**kwargs):
        super(RenderModule,self).__init__(schema_type = RenderParameters,*args,**kwargs)
        print self.args
        self.render=renderapi.render.connect(**self.args['render'])

if __name__ == '__main__':
    example_input={
        "render":{
            "host":"ibs-forrestc-ux1",
            "port":8080,
            "owner":"NewOwner",
            "project":"H1706003_z150",
            "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
        }
    }
    module = RenderModule(input_data=example_input)
    module.run()

    bad_input={
        "render":{
            "host":"ibs-forrestc-ux1",
            "port":'8080',
            "owner":"Forrest",
            "project":"H1706003_z150",
            "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
        }
    }
    module = RenderModule(input_data=bad_input)
    module.run()
