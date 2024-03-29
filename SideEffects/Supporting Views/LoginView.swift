//
//  LoginView.swift
//  SideEffects
//
//  Created by Kevin Tran on 11/15/19.
//  Copyright © 2019 Kevin Tran. All rights reserved.
//

import SwiftUI

struct LoginView: View {
    @State private var showingAlert = false
    @State var selection: Int? = nil
    
    @EnvironmentObject var loginData: LoginData
    @State private var networkManager = NetworkManager()
    
    var body: some View {
        VStack {
            Text("Side Effects").font(Font.system(size: 60, design: .default))
            
            HStack {
                Text("Username")
                TextField("Username", text: $loginData.username, onEditingChanged: { isEditing in
                    }).foregroundColor(.primary).padding().textFieldStyle(RoundedBorderTextFieldStyle())

                Button(action: {
                    self.loginData.username = ""
                }) {
                    Image(systemName: "xmark.circle.fill").opacity(loginData.username == "" ? 0 : 1)
                }
            }.padding()
            
            HStack {
                Text("Password")
                SecureField("Enter a password", text: $loginData.password)
                    .foregroundColor(.primary).padding().textFieldStyle(RoundedBorderTextFieldStyle())

                Button(action: {
                    self.loginData.password = ""
                }) {
                    Image(systemName: "xmark.circle.fill").opacity(loginData.password == "" ? 0 : 1)
                }
            }.padding()
            
            NavigationLink(destination: MainView(networkManager: self.$networkManager), tag: 1, selection: $selection) {
                Button(action: {
                    self.networkManager.post(code: 1, uploadData: self.loginData.create_keys_values(), completionHandler: { flag, data  in
                        if flag == true {
                            self.networkManager.decodeThread(data: data!)
                            self.selection = 1
                        }
                        else {
                            self.showingAlert = true
                        }
                    })
                })
                {
                    Text("Submit")
                        .padding()
                        .foregroundColor(.white)
                        .background(LinearGradient(gradient: Gradient(colors: [Color.red,  Color.purple]), startPoint: .leading, endPoint: .trailing))
                        .cornerRadius(40)
                }.alert(isPresented: $showingAlert) {
                    Alert(title: Text("Login"), message: Text("Incorrect Username and Password"), dismissButton:
                        .default(Text("Okay")))
                }
            }
        }
    }
}

struct LoginView_Previews: PreviewProvider {
    static var previews: some View {
        LoginView()
    }
}
