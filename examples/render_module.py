from json_module import JsonModule

class RenderModule(JsonModule):
    
    def __init__(self,input=None,schema_extension=None):
        schema = {
            "description":"a generic module for interacting with render",
            "properties":{
                "render":{
                    "type":"object",
                    "title":"Render Parameters",
                    "description":"This specifies parameters for connecting to render host",
                    "properties":{
                        "host":{
                            "type":"string",
                            "description":"url of render host"
                            },
                        "port":{
                            "type":"integer",
                            "description":"port of render host"
                            },
                        "owner":{
                            "type":"string",
                            "description":"name of default render owner"
                        },
                        "project":{
                            "type":"string",
                            "description":"name of default render project"
                        },
                        "client_scripts":{
                            "type": "string",
                            "format": "input_path",
                            "description":"path to render client scripts"
                        }                        
                    },
                    "required": [ "host", "port", "owner", "project", "client_scripts" ]                
                }
            }
        }
        schema=self.add_to_schema(schema,schema_extension)
        JsonModule.__init__(self,input=input,schema_extension=schema)
        #self.render = renderapi.render.connect(**self.args['render'])

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
    module = RenderModule(input=example_input)
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
    module = RenderModule(input=bad_input)
    module.run()
