# This script was executed inside July Ruby IDE to verify interactive execution flow.

# July Ruby IDE動作確認用のサンプルコードです。

puts "🃏 カード引きゲーム開始！"
puts "Enterキーを押すとカードを引けます（終了する場合は exit と入力）"

cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "JOKER"]

loop do
  input = gets.chomp
  break if input == "exit"

  if cards.empty?
    puts "Error: カードがありません。"
    next
  end

  card = cards.sample

  if card == "JOKER"
    puts "💀 ジョーカーだ…！GAME OVER！"
  else
    puts "🃏 引いたカードは [#{card}] です。"
  end

  cards.delete(card)

  puts "もう一回引きますか？（Enter / exit）"
end

puts "ゲーム終了、お疲れさまでした。"
