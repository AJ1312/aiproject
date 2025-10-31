package cmd

import (
	"cli-top/debug"
	"cli-top/login"
	"fmt"
	"strings"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

// var username = "k"
// var password = "k"
// var regno = "k"

var credCmd = &cobra.Command{
	Use:   "login",
	Short: "Login to VTOP",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("NOTE: Your password will be visible.")
		username := promptInput("Enter your username: ")
		password := promptInput("Enter your password: ")
		key := GenerateAESKey()

		encryptedPassword, err := encryptPassword(password, key)
		if err != nil && debug.Debug {
			fmt.Println("Error encrypting password:", err)
			return
		}

		fmt.Printf("Logging in with username: %s\n", strings.ToUpper(username))

		// Perform actual login to get cookies
		fmt.Println("Connecting to VTOP...")
		loginSecrets := login.Login(strings.ToUpper(username), password)
		cookies, regNo := login.HomePage(loginSecrets)

		if regNo == "" {
			fmt.Println("Login failed. Please check your credentials and try again.")
			if debug.Debug {
				fmt.Printf("Cookies received: %+v\n", cookies)
			}
			return
		}

		fmt.Printf("✅ Login successful! Registration Number: %s\n", regNo)

		// Save all credentials and cookies
		viper.Set("VTOP_USERNAME", "\""+strings.ToUpper(username)+"\"")
		viper.Set("PASSWORD", "\""+encryptedPassword+"\"")
		viper.Set("KEY", "\""+key+"\"")
		viper.Set("CSRF", "\""+cookies.CSRF+"\"")
		viper.Set("JSESSIONID", "\""+cookies.JSESSIONID+"\"")
		viper.Set("SERVERID", "\""+cookies.SERVERID+"\"")
		viper.Set("REGNO", "\""+regNo+"\"")

		if err := viper.WriteConfigAs("cli-top-config.env"); err != nil && debug.Debug {
			fmt.Println("Error writing to .env file:", err)
			return
		}

		fmt.Println("Credentials and session saved successfully.")
	},
}

func promptInput(prompt string) string {
	fmt.Print(prompt)
	var input string
	fmt.Scanln(&input)
	return input
}

func init() {
	credCmd.Flags().String("username", "", "Enter VTOP username")
	credCmd.Flags().String("password", "", "Enter VTOP password")
	credCmd.Flags().String("regno", "", "Enter VIT registration number")
	viper.SetConfigType("env")
	viper.SetConfigFile("cli-top-config.env")
	viper.ReadInConfig()
	rootCmd.AddCommand(credCmd)
}
