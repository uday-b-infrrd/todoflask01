class Format:
    def toJsonFormat(self,row_header,sql_data):
        self.json_data=[]
        for row in sql_data:
            self.json_data.append(dict(zip(row_header,row)))
        return self.json_data
