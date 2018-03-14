require 'discordrb'
require 'byebug'
require 'json'

PUBG_TRACKER_BASE_URL = "https://api.pubgtracker.com/v2/profile/pc/"

file = File.read('bot_info.json')
data_hash = JSON.parse(file)

bot = Discordrb::Bot.new token: data_hash['TOKEN'], client_id: data_hash['CLIENT_ID']

def self.pubg_tracker_request(account_name, key)
  uri = URI(PUBG_TRACKER_BASE_URL + account_name)
  req = Net::HTTP::Get.new(uri)
  req["TRN-Api-Key"] = key

  res = Net::HTTP.start(uri.hostname) {|http|
    http.request(req)
  }

  JSON.parse res.body, symbolize_names: true
end

bot.message(with_text: '!howlong-help') do |event|
    event.respond 'Type "howlong" and then mention a specific user in the channel'
    event.respond 'Example:'
    event.respond '"howlong"'
    event.respond '@Jabronious'
end

bot.message(with_text: '!howlong') do |event|
    event.respond 'What is the PUBG Username of the user?'
    event.user.await(:user) do |user_mention|
        res = pubg_tracker_request(user_mention.content, data_hash['PUBG_TRACKER_KEY'])
        event.respond res[:error] if res[:error]
    end
end

bot.run